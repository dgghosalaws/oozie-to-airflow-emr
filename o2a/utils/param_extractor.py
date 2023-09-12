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
"""Extract params from oozie's action node"""
from _elementtree import Element

from o2a.o2a_libs import el_parser
from o2a.utils import xml_utils

TAG_PARAM = "param"


def extract_param_values_from_action_node(oozie_node: Element ,paramidentifier: str = '-d'):
    param_nodes = xml_utils.find_nodes_by_tag(oozie_node, TAG_PARAM)
    param_args = ""
    new_params = {}
    new_args = []
    for node in param_nodes:
        if not node.text:
            continue
        param = el_parser.translate(node.text)
        key, _, value = param.partition("=")
        new_params[key] = value
        new_args.append(paramidentifier)
        param_args = key + "=" + value
        new_args.append(param_args)
        # param_args += key+ "="+value+" -d "
    # print(param_args)
    return new_args
    # return param_args[:-1]
