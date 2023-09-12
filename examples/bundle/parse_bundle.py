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
import os
import xml.etree.ElementTree as ET
from shutil import copyfile

# location of oozie-to-airflow repo
o2a_home="/Users/dgghosal/Documents/proserve/projects/gitlab_proserv/oozie-to-airflow" #for ex.

bundle_file='bundle-demo_offer_outreach.xml'
bundle_name=os.path.basename(bundle_file).split('.')[0]
print(f"Parsing for bundle: {bundle_file}")
bundle_tree = ET.parse(bundle_file)
bundle_root = bundle_tree.getroot()
for node in bundle_tree.iter():
    # Strip namespaces
    node.tag = node.tag.split("}")[1][0:]

#Extract coordinator and replace with OS valid path
#Absolute path of co-ordinator xml file
coordinator_list=[]
for node in bundle_root.iter():
    if node.tag == 'coordinator':
        if node[0].tag == 'app-path':
            coordinator_list.append((node[0].text))

for coordinator_file in coordinator_list:
    print(f"Parsing coordinator: {coordinator_file}.")
    coordinator_name=os.path.basename(coordinator_file).split('.')[0]
    coordinator_tree = ET.parse(coordinator_file)
    coordinator_root = coordinator_tree.getroot()
    for node in coordinator_tree.iter():
        # Strip namespaces
        node.tag = node.tag.split("}")[1][0:]
    dataset_dict={}
    input_dataset_lst = []
    # Parse dataset, extract wofkflow xml, and properties
    for node in coordinator_root.iter():
        if node.tag == 'datasets':
            #dataset_dict={}
            for dataset in node.iter():
                if dataset.tag == 'dataset':
                    dataset_name=dataset.get('name')
                    dataset_frequency=dataset.get('frequency')
                if dataset.tag == 'uri-template':
                    dataset_uri=dataset.text
                    dataset_dict[dataset_name]=[dataset_frequency,dataset_uri]
        if node.tag == 'action':
            for child in node.iter():
                if child.tag == 'app-path':
                    workflow_xml = child.text
        if node.tag == 'input-events':
            #input_dataset_lst = []
            for data_in in node.iter():
                if data_in.tag == 'data-in':
                    for instance in data_in.iter():
                        if instance.tag == 'instance':
                            data_instance = instance.text
                            start_instance = 'n/a'
                            end_instance = 'n/a'
                        else:
                            if instance.tag == 'start-instance':
                                start_instance = instance.text
                                data_instance = 'n/a'
                            if instance.tag == 'end-instance':
                                end_instance = instance.text
                        #todo -- check if start and end instance are different and also add logic if there is just instance tag instead of start and end both tag
                    input_dataset_lst.append(data_in.get('dataset')+'|'+start_instance+'|'+end_instance+'|'+ data_instance + '|' + coordinator_name+'|'+bundle_name)
        if node.tag == 'configuration':
            job_prop_lst = []
            for config_child in node.iter():
                if config_child.tag == 'property':
                    job_prop_lst.append(config_child[0].text+"="+config_child[1].text)

    DAG_NAME=os.path.basename(workflow_xml).split('.')[0].replace('workflow-','')
    print(DAG_NAME)
    o2p_dir_hdfs= o2a_home + '/examples/' + DAG_NAME + '/hdfs'

    os.makedirs(o2p_dir_hdfs,exist_ok=True)
    o2p_dir_base=  o2a_home + '/examples/' + DAG_NAME

    workflow_file_to_convert=o2p_dir_hdfs +'/workflow.xml'
    copyfile(workflow_xml,workflow_file_to_convert)

    static_config_prop = 'configuration.properties'

    copyfile(static_config_prop,o2p_dir_base+'/configuration.properties')

    dag_job_prop_file=o2p_dir_base+'/job.properties'

    static_job_prop="""
nameNode=s3_bucket_name_for_script+
examplesRoot=examples
oozie.use.system.libpath = true
oozie.wf.application.path=${nameNode}/user/${user.name}/${examplesRoot}/apps/subwf
    """
    f = open(dag_job_prop_file, "w")
    f.write("%s\n" % static_job_prop)
    for job_prop in job_prop_lst:
        f.write('%s\n' % job_prop)
    f.close()

    cmd_to_run =  o2a_home + "/bin/o2a -i " \
        + o2a_home +"/examples/"+ DAG_NAME + " -o " \
        + o2a_home + "/output/" + DAG_NAME + " -x 0.4 -n " +  DAG_NAME
    #print(cmd_to_run)
    os.system(cmd_to_run)


    final_out_dag_file= o2a_home + "/output/" + DAG_NAME + '/' + DAG_NAME + '.py'
