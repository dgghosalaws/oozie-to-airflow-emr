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
"""PropertyParser"""
import os
import xml.etree.ElementTree as ET

from o2a.converter.workflow import Workflow
from o2a.o2a_libs.property_utils import PropertySet
from o2a.utils import el_utils
from o2a.utils.constants import CONFIG, JOB_PROPS
from o2a.converter.constants import HDFS_FOLDER


class PropertyParser:
    """
    Parse configuration.properties and job.properties to PropertySet
    """

    def __init__(self, workflow: Workflow, props: PropertySet):
        self.config_file = os.path.join(workflow.input_directory_path, CONFIG)
        self.coordinator_file = os.path.join(workflow.input_directory_path, HDFS_FOLDER, "coordinator.xml")
        self.job_properties_file = os.path.join(workflow.input_directory_path, JOB_PROPS)
        self.props = props

    def parse_property(self):
        self.read_and_update_job_properties_replace_el()
        self.read_config_replace_el()

    def read_config_replace_el(self):
        """
        Reads configuration properties to config dictionary.
        Replaces EL properties within.

        :return: None
        """
        self.props.config = el_utils.extract_evaluate_properties(
            properties_file=self.config_file, props=self.props
        )

    def read_and_update_job_properties_replace_el(self):
        """
        Reads job properties and updates job_properties dictionary with the read values
        Replaces EL job_properties within.

        :return: None
        """

        """
        If coordinator file exists, extracts properties from configuration tag and append job.properties file
        """

        if os.path.isfile(self.coordinator_file):
            file_tree = ET.parse(self.coordinator_file)
            coordinator_root = file_tree.getroot()
            for node in file_tree.iter():
                # Strip namespaces
                node.tag = node.tag.split("}")[1][0:]
            tag_list = {elem.tag for elem in coordinator_root.iter()}
            if 'coordinator-app' in tag_list:
                print(f"file: {self.coordinator_file} is oozie coordinator")
                for node in coordinator_root.iter():
                    if node.tag == 'configuration':
                        job_prop_lst = []
                        for config_child in node.iter():
                            if config_child.tag == 'property':
                                job_prop_lst.append(config_child[0].text+"="+config_child[1].text)
                prop_file_append = open(self.job_properties_file, 'a')
                for job_prop in job_prop_lst:
                    prop_file_append.write('%s\n' % job_prop)
                prop_file_append.close()
            else:
                print(f"file: {self.coordinator_file} is not oozie coordinator")
        else:
            print('coordinator file does not exist')

        self.props.job_properties.update(
            el_utils.extract_evaluate_properties(properties_file=self.job_properties_file, props=self.props)
        )
