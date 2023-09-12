# -*- coding: utf-8 -*-
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

#Modifications Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import ast
from typing import TYPE_CHECKING, Any, Sequence

from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.providers.amazon.aws.links.emr import EmrClusterLink
from airflow.utils.helpers import exactly_one
from o2a.o2a_libs.hooks.emr import EmrHook
from o2a.o2a_libs.utils.waiter import waiter

if TYPE_CHECKING:
    from airflow.utils.context import Context

from airflow.compat.functools import cached_property


class EmrSubmitAndMonitorStepOperator(BaseOperator):
    """
    An operator that adds steps to an existing EMR job_flow.

    .. seealso::
        For more information on how to use this operator, take a look at the guide:
        :ref:`howto/operator:EmrAddStepsOperator`

    :param job_flow_id: id of the JobFlow to add steps to. (templated)
    :param job_flow_name: name of the JobFlow to add steps to. Use as an alternative to passing
        job_flow_id. will search for id of JobFlow with matching name in one of the states in
        param cluster_states. Exactly one cluster like this should exist or will fail. (templated)
    :param cluster_states: Acceptable cluster states when searching for JobFlow id by job_flow_name.
        (templated)
    :param aws_conn_id: aws connection to uses
    :param steps: boto3 style steps or reference to a steps file (must be '.json') to
        be added to the jobflow. (templated)
    :param wait_for_completion: If True, the operator will wait for all the steps to be completed.
    :param execution_role_arn: The ARN of the runtime role for a step on the cluster.
    :param do_xcom_push: if True, job_flow_id is pushed to XCom with key job_flow_id.
    """

    template_fields: Sequence[str] = (
        "job_flow_id",
        "job_flow_name",
        "cluster_states",
        "steps",
        "execution_role_arn",
    )
    template_ext: Sequence[str] = (".json",)
    template_fields_renderers = {"steps": "json"}
    ui_color = "#f9c915"
    operator_extra_links = (EmrClusterLink(),)

    def __init__(
        self,
        *,
        job_flow_id: str | None = None,
        job_flow_name: str | None = None,
        cluster_states: list[str] | None = None,
        aws_conn_id: str = "aws_default",
        steps: list[dict] | str | None = None,
        wait_for_completion: bool = True,
        waiter_delay: int | None = None,
        waiter_max_attempts: int | None = None,
        execution_role_arn: str | None = None,
        **kwargs,
    ):
        if not exactly_one(job_flow_id is None, job_flow_name is None):
            raise AirflowException("Exactly one of job_flow_id or job_flow_name must be specified.")
        super().__init__(**kwargs)
        cluster_states = cluster_states or []
        steps = steps or []
        self.aws_conn_id = aws_conn_id
        self.job_flow_id = job_flow_id
        self.job_flow_name = job_flow_name
        self.cluster_states = cluster_states
        self.steps = steps
        self.wait_for_completion = wait_for_completion
        self.waiter_delay = waiter_delay
        self.waiter_max_attempts = waiter_max_attempts
        self.execution_role_arn = execution_role_arn

    def execute(self, context: Context) -> list[str]:
        emr_hook = EmrHook(aws_conn_id=self.aws_conn_id)

        job_flow_id = self.job_flow_id or emr_hook.get_cluster_id_by_name(
            str(self.job_flow_name), self.cluster_states
        )

        if not job_flow_id:
            raise AirflowException(f"No cluster found for name: {self.job_flow_name}")

        if self.do_xcom_push:
            context["ti"].xcom_push(key="job_flow_id", value=job_flow_id)

        EmrClusterLink.persist(
            context=context,
            operator=self,
            region_name=emr_hook.conn_region_name,
            aws_partition=emr_hook.conn_partition,
            job_flow_id=job_flow_id,
        )

        self.log.info("Adding steps to %s", job_flow_id)

        # steps may arrive as a string representing a list
        # e.g. if we used XCom or a file then: steps="[{ step1 }, { step2 }]"
        steps = self.steps
        if isinstance(steps, str):
            steps = ast.literal_eval(steps)
        return emr_hook.add_job_flow_steps(
            job_flow_id=job_flow_id,
            steps=steps,
            wait_for_completion=self.wait_for_completion,
            waiter_delay=self.waiter_delay,
            waiter_max_attempts=self.waiter_max_attempts,
            execution_role_arn=self.execution_role_arn,
        )

class EmrCreateJobFlowOperator(BaseOperator):
    """
    Creates an EMR JobFlow, reading the config from the EMR connection.
    A dictionary of JobFlow overrides can be passed that override
    the config from the connection.
    .. seealso::
        For more information on how to use this operator, take a look at the guide:
        :ref:`howto/operator:EmrCreateJobFlowOperator`
    :param aws_conn_id: The Airflow connection used for AWS credentials.
        If this is None or empty then the default boto3 behaviour is used. If
        running Airflow in a distributed manner and aws_conn_id is None or
        empty, then default boto3 configuration would be used (and must be
        maintained on each worker node)
    :param emr_conn_id: :ref:`Amazon Elastic MapReduce Connection <howto/connection:emr>`.
        Use to receive an initial Amazon EMR cluster configuration:
        ``boto3.client('emr').run_job_flow`` request body.
        If this is None or empty or the connection does not exist,
        then an empty initial configuration is used.
    :param job_flow_overrides: boto3 style arguments or reference to an arguments file
        (must be '.json') to override specific ``emr_conn_id`` extra parameters. (templated)
    :param region_name: Region named passed to EmrHook
    :param wait_for_completion: Whether to finish task immediately after creation (False) or wait for jobflow
        completion (True)
    :param waiter_countdown: Max. seconds to wait for jobflow completion (only in combination with
        wait_for_completion=True, None = no limit)
    :param waiter_check_interval_seconds: Number of seconds between polling the jobflow state. Defaults to 60
        seconds.
    """

    template_fields: Sequence[str] = ("job_flow_overrides",)
    template_ext: Sequence[str] = (".json",)
    template_fields_renderers = {"job_flow_overrides": "json"}
    ui_color = "#f9c915"
    operator_extra_links = (EmrClusterLink(),)

    def __init__(
        self,
        *,
        aws_conn_id: str = "aws_default",
        emr_conn_id: str | None = "emr_default",
        job_flow_overrides: str | dict[str, Any] | None = None,
        region_name: str | None = None,
        wait_for_completion: bool = False,
        waiter_countdown: int | None = None,
        waiter_check_interval_seconds: int = 60,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.aws_conn_id = aws_conn_id
        self.emr_conn_id = emr_conn_id
        self.job_flow_overrides = job_flow_overrides or {}
        self.region_name = region_name
        self.wait_for_completion = wait_for_completion
        self.waiter_countdown = waiter_countdown
        self.waiter_check_interval_seconds = waiter_check_interval_seconds
        self._job_flow_id: str | None = None

    @cached_property
    def _emr_hook(self) -> EmrHook:
        """Create and return an EmrHook."""
        return EmrHook(
            aws_conn_id=self.aws_conn_id, emr_conn_id=self.emr_conn_id, region_name=self.region_name
        )

    def execute(self, context: Context) -> str | None:
        self.log.info(
            "Creating job flow using aws_conn_id: %s, emr_conn_id: %s", self.aws_conn_id, self.emr_conn_id
        )
        if isinstance(self.job_flow_overrides, str):
            job_flow_overrides: dict[str, Any] = ast.literal_eval(self.job_flow_overrides)
            self.job_flow_overrides = job_flow_overrides
        else:
            job_flow_overrides = self.job_flow_overrides
        response = self._emr_hook.create_job_flow(job_flow_overrides)

        if not response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            raise AirflowException(f"Job flow creation failed: {response}")
        else:
            self._job_flow_id = response["JobFlowId"]
            self.log.info("Job flow with id %s created", self._job_flow_id)
            EmrClusterLink.persist(
                context=context,
                operator=self,
                region_name=self._emr_hook.conn_region_name,
                aws_partition=self._emr_hook.conn_partition,
                job_flow_id=self._job_flow_id,
            )

            if self.wait_for_completion:
                # Didn't use a boto-supplied waiter because those don't support waiting for WAITING state.
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/emr.html#waiters
                waiter(
                    get_state_callable=self._emr_hook.get_conn().describe_cluster,
                    get_state_args={"ClusterId": self._job_flow_id},
                    parse_response=["Cluster", "Status", "State"],
                    # Cluster will be in WAITING after finishing if KeepJobFlowAliveWhenNoSteps is True
                    desired_state={"WAITING", "TERMINATED"},
                    failure_states={"TERMINATED_WITH_ERRORS"},
                    object_type="job flow",
                    action="finished",
                    countdown=self.waiter_countdown,
                    check_interval_seconds=self.waiter_check_interval_seconds,
                )

            return self._job_flow_id

    def on_kill(self) -> None:
        """
        Terminate the EMR cluster (job flow). If TerminationProtected=True on the cluster,
        termination will be unsuccessful.
        """
        if self._job_flow_id:
            self.log.info("Terminating job flow %s", self._job_flow_id)
            self._emr_hook.conn.terminate_job_flows(JobFlowIds=[self._job_flow_id])
