<!--
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
 -->

## About
Code sample and script in this folder shows how to parse bundle xml file, coordinator xml and use this utility to convert its workflow to Airflow DAGs.
Parser code in this folder is not part of core utility code.
This document explains how a typical bundle can be parsed recursively (parse each coordinator, extract properties, and use utility to convert to Airflow DAG)


# Setup
###### Pre Req: Utility is configured and running per instructions.

This folder contains an example bundle which has two coordinators (and its workflow).
```
├── bundle-demo_offer_outreach.xml
├── configuration.properties
├── coordinator-demo_offer_outreach.xml
├── coordinator-demo_offer_outreach_tx.xml
├── parse_bundle.py
├── workflow-demo_offer_outreach.xml
└── workflow-demo_offer_outreach_tx.xml
```
In script: `parse_bundle.py`, modify value of `o2a_home` to where utility is downloaded for ex.:
`o2a_home="/Users/dgghosal/Documents/proserve/projects/gitlab_proserv/oozie-to-airflow"`

In this example bundle, coordinator and workflow code are in same folder but if these are in different folder in repo, corresponding changes to ` parse_bundle.py` would be required.
# Running bundle parser
Run parser script in same python environment in which utility is installed.
```
python parse_bundle.py
```
Script will create DAGs (with name same as that of workflow) in output folder in utility
```
output/
├── demo_offer_outreach
│   └── demo_offer_outreach.py
└── demo_offer_outreach_tx
    └── demo_offer_outreach_tx.py
```
