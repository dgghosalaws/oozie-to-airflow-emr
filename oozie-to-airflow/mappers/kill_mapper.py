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
"""Kill mapper - maps the workflow end"""
from typing import Set, List

from converter.primitives import Workflow, Task, Relation
from mappers.base_mapper import BaseMapper
from utils.template_utils import render_template


class KillMapper(BaseMapper):
    """
    Converts a Kill Oozie node to an Airflow task.
    """

    def convert_to_text(self) -> str:
        tasks = [
            Task(
                task_id=self.name,
                template_name="kill.tpl",
                template_params=dict(trigger_rule=self.trigger_rule),
            )
        ]
        relations: List[Relation] = []
        return render_template(template_name="action.tpl", tasks=tasks, relations=relations)

    def required_imports(self) -> Set[str]:
        return {"from airflow.operators import bash_operator"}

    def on_parse_finish(self, workflow: Workflow):
        super().on_parse_finish(workflow)
        if workflow.nodes[self.name].is_error:
            del workflow.nodes[self.name]
            workflow.relations -= {
                relation for relation in workflow.relations if relation.to_task_id == self.name
            }
