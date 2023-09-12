{#
  Copyright 2019 Google LLC

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
  SPDX-License-Identifier: Apache-2.0
 #}

{#
  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
  SPDX-License-Identifier: Apache-2.0
#}
{% import "macros/props.tpl" as props_macro %}
{{ task_id | to_var }} = EmrSubmitAndMonitorStepOperator(
    task_id={{ task_id | to_python }},
    steps = [{'Name': {{ task_id | to_python }},'ActionOnFailure': 'CONTINUE','HadoopJarStep': {'Jar': 'command-runner.jar','Args': {{ step | to_python }},},}],
    job_flow_id=CONFIG['emr_cluster'],
    aws_conn_id=CONFIG['aws_conn_id'],
)
