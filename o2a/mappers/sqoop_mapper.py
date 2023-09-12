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

#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: Apache-2.0
"""Maps Sqoop Oozie node to Airflow's DAG"""
from typing import Dict, List, Optional, Set

from xml.etree.ElementTree import Element

from o2a.converter.task import Task
from o2a.converter.relation import Relation
from o2a.mappers.action_mapper import ActionMapper
from o2a.mappers.extensions.prepare_mapper_extension import PrepareMapperExtension
from o2a.o2a_libs.property_utils import PropertySet
from o2a.utils.file_archive_extractors import ArchiveExtractor, FileExtractor
from o2a.utils.xml_utils import get_tag_el_text

TAG_TRACKER = "job-tracker"
TAG_NAME = "name-node"
TAG_COMMAND = "command"


# pylint: disable=too-many-instance-attributes
class SqoopMapper(ActionMapper):
    """
    Converts a Sqoop Oozie node to an Airflow task.
    """

    def __init__(self, oozie_node: Element, name: str, props: PropertySet, **kwargs):
        ActionMapper.__init__(self, oozie_node=oozie_node, name=name, props=props, **kwargs)
        self.params_dict: Dict[str, str] = {}
        self.file_extractor = FileExtractor(oozie_node=oozie_node, props=self.props)
        self.archive_extractor = ArchiveExtractor(oozie_node=oozie_node, props=self.props)
        self._parse_oozie_node()
        self.step: Optional[str] = []
        self.prepare_extension: PrepareMapperExtension = PrepareMapperExtension(self)

    def _parse_oozie_node(self):
        self.job_tracker = get_tag_el_text(self.oozie_node, TAG_TRACKER)
        self.name_node = get_tag_el_text(self.oozie_node, TAG_NAME)
        self.command = get_tag_el_text(self.oozie_node, TAG_COMMAND)
        self.sqoop_step = self.command.split()
        self.sqoop_step.insert(0, "sqoop")
        self.files, self.hdfs_files = self.file_extractor.parse_node()
        self.archives, self.hdfs_archives = self.archive_extractor.parse_node()

    def to_tasks_and_relations(self):
        action_task = Task(
            task_id=self.name,
            template_name="sqoop.tpl",
            template_params=dict(
                props=self.props,
                step=self.sqoop_step,
                action_node_properties=self.props.action_node_properties,
            ),
        )
        tasks = [action_task]
        relations: List[Relation] = []
        prepare_task = self.prepare_extension.get_prepare_task()
        if prepare_task:
            tasks, relations = self.prepend_task(prepare_task, tasks, relations)
        return tasks, relations

    @staticmethod
    def _validate_paths(input_directory_path, output_directory_path):
        if not input_directory_path:
            raise Exception(f"The input_directory_path should be set and is {input_directory_path}")
        if not output_directory_path:
            raise Exception(f"The output_directory_path should be set and is {output_directory_path}")

    def required_imports(self) -> Set[str]:
        return {
            "from airflow.utils import dates",
            "from o2a.o2a_libs.operator.emr_submit_and_monitor_step_operator import "
            "EmrSubmitAndMonitorStepOperator",
        }
