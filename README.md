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

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

  - [Credit](#credit)
- [Oozie to Airflow](#oozie-to-airflow)
- [Road Map](#road-map)
- [Running the Program](#running-the-program)
  - [Installing from sources](#installing-from-sources)
  - [Running the conversion](#running-the-conversion)
  - [Structure of the application folder](#structure-of-the-application-folder)
  - [The o2a libraries](#the-o2a-libraries)
- [Environment for Oozie to Airflow conversion](#environment-for-oozie-to-airflow-conversion)
  - [Environment setup](#environment-setup)
- [Examples](#examples)
  - [Hive Example](#hive-example)
  - [Spark Example](#spark-example)
  - [Sqoop Example](#sqoop-example)
  - [Java Example](#java-example)
  - [Pig/Hive Example](#pighive-example)
  - [Sub Workflow Example](#sub-workflow-example)
  - [Coordinator Example](#coordinator-example)
- [Deployment Instructions](#deployment-instructions)
  - [Bundle Parser](#bundle-parser)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

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

## Credit
This utility has been created by modifying the Open source Utility -> https://github.com/GoogleCloudPlatform/oozie-to-airflow

# Oozie to Airflow
A framework to convert between [Apache Oozie](http://oozie.apache.org/) workflows
and [Apache Airflow](https://airflow.apache.org) workflows.

The program targets Apache Airflow >= 1.10 and Apache Oozie 0.4/1.0 XML schema.
Current build is targeted to support all Hive mappings.


# Road Map


# Running the Program

Note that you need Python >= 3.6 to run the converter. The utility has been tested with Python = 3.9
The  utility uses a custom Airflow operator [EmrSubmitAndMonitorStepOperator](oozie-to-airflow/o2a/o2a_libs/operator/emr_submit_and_monitor_step_operator.py) to submit EMR Steps.

## Installing from sources

1. (Optional) Install virtualenv:

    In case you use sources of `o2a`, the environment can be set up via the virtualenv setup
(you can create one using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)
for example).

2. Install oozie-to-airflow - you have 2 options to do so:

    1. automatically: install `o2a` from local folder using `pip install -e .` - NEED TO PROVIDE AUTO SETUP

        This will take care about, among others, adding the [bin](bin) subdirectory to the PATH.

    2. more manually:

        1. While in your virtualenv, you can install all the requirements via `pip install -r requirements.txt`.

        2. You can add the [bin](bin) subdirectory to your
        PATH, then all the scripts below can be run without adding the `./bin` prefix.
        This can be done for example by adding a line similar to the one below to your `.bash_profile`
        or `bin/postactivate` from your virtual environment:

        ```bash
        export PATH=${PATH}:<INSERT_PATH_TO_YOUR_OOZIE_PROJECT>/bin
        ```

        Otherwise you need to run all the scripts from the bin subdirectory, for example:

        ```bash
        ./bin/o2a --help
        ```

In all the example commands below, it is assumed that the [bin](bin) directory is in your PATH

## Running the conversion

You can run the program by calling:
`o2a -i <INPUT_APPLICATION_FOLDER> -o <OUTPUT_FOLDER_PATH>`

Example:
`o2a -i examples/hive -o output/hive`

This is the full usage guide, available by running `o2a -h`

```
usage: o2a [-h] -i INPUT_DIRECTORY_PATH -o OUTPUT_DIRECTORY_PATH
                      [-n DAG_NAME] [-u USER] [-s START_DAYS_AGO]
                      [-x SCHEMA_VERSION] [-v SCHEDULE_INTERVAL] [-d]

Convert Apache Oozie workflows to Amazon Managed Workflows on Apache Airflow.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIRECTORY_PATH, --input-directory-path INPUT_DIRECTORY_PATH
                        Path to input directory
  -o OUTPUT_DIRECTORY_PATH, --output-directory-path OUTPUT_DIRECTORY_PATH
                        Desired output directory
  -n DAG_NAME, --dag-name DAG_NAME
                        Desired DAG name [defaults to input directory name]
  -u USER, --user USER  The user to be used in place of all ${user.name}
                        [defaults to user who ran the conversion]
  -s START_DAYS_AGO, --start-days-ago START_DAYS_AGO
                        Desired DAG start as number of days ago
  -x SCHEMA_VERSION, --schema-version SCHEMA_VERSION
                        Desired Oozie all schema version.[1.0,0.4]
  -v SCHEDULE_INTERVAL, --schedule-interval SCHEDULE_INTERVAL
                        Desired DAG schedule interval as number of days
  -d, --dot             Renders workflow files in DOT format

```

## Structure of the application folder

The input application directory has to follow the structure defined as follows:

```
<APPLICATION>/
             |- job.properties        - job properties that are used to run the job
             |- hdfs                  - folder with application - should be copied to HDFS
             |     |- workflow.xml    - Oozie workflow xml (1.0 schema)
             |     |- ...             - additional folders required to be copied to HDFS
             |- configuration.template.properties - template of configuration values used during conversion
             |- configuration.properties          - generated properties for configuration values
```

## The o2a libraries

Converted Airflow DAGs use common libraries. Those libraries should be available on PYTHONPATH for all
Airflow components - scheduler, webserver and workers - so that they can be imported when DAGs are parsed.

Those libraries are in [o2a/o2a_libs](oozie-to-airflow/o2a/o2a_libs) folder and the easiest way to make them available to
all the DAGs is to copy them (preserving o2a parent directory) to the "dags" folder of Airflow.


# Environment for Oozie to Airflow conversion

## Environment setup

An easy way of running the workflows of Oozie as well as running the oozie-to-airflow converted DAGs in
Airflow is by using Airflow on EC2 and Amazon EMR.


### Setup on Managed Workflow for Apache Airflow
MWAA expects the following structure.

```
<airflow-bucket/dags>/
             |- .airflowignore        - contains .o2a to be ignored
             |- o2a          - Utility Library
             |- dag.py          - generated dag after running the converter
```

### EMR Cluster with Oozie. Include other applications as referred in oozie workflows. Ex: Pig,Spark etc.

* Create EMR cluster with Oozie.

Those are the steps you should follow to set it up:

1. Create a EMR cluster
2. Set up all required [Airflow Connections](https://airflow.apache.org/howto/connection/index.html)
   in Airflow.




# Examples

All examples can be found in the [examples](oozie-to-airflow/examples) directory.

* [Hive](#hive-example)
* [Spark](#spark-example)
* [Pig/Hive](#pig/hive-example)
* [Sub Workflow](#sub-workflow-example)
* [Scoop](#sqoop-example)
* [Java](#java-example)
* [Coordinator](#coordinator-example)
* [Bundle](#bundle-parser)

## Hive Example

### Prerequisites

Make sure to first copy `/examples/hive/configuration.template.properties`, rename it as
`configuration.properties` and fill in with configuration data.
Required configuration items are


```properties
            #emr_cluster={{EMR_CLUSTER_ID}}
            emr_cluster=j-3JT1C4X61EFH
            aws_conn_id=aws_default
            aws_region=us-west-2
            check_interval=30
            s3_uri_prefix=s3://pinwheel-dipankar/dags
```
Modify the s3_uri_prefix and emr_cluster details.

Edit and verify contents of `workflow.xml`

```xml
     <script>script.q</script>
    <param>INPUT=s3://pinwheel-dipankar/data/input/</param>
    <param>OUTPUT=s3://pinwheel-dipankar/data/output/output-data/</param>
```

### Running

The Hive example can be run as:

`o2a -i examples/hive -o output/hive`


### Output
In this example the output will be created in the `./output/hive/` folder.


## Spark Example

### Prerequisites

Make sure to first copy `/examples/spark/configuration.template.properties`, rename it as
`configuration.properties` and fill in with configuration data.
Required configuration items are


```properties
            #emr_cluster={{EMR_CLUSTER_ID}}
            emr_cluster=j-3JT1C4X61EFH
            aws_conn_id=aws_default
            aws_region=us-west-2
            check_interval=30
            s3_uri_prefix=s3://pinwheel-dipankar/dags
```
Modify the s3_uri_prefix and emr_cluster details.

Verify contents of `workflow.xml`

```xml
  <spark-opts>--executor-memory 20G --num-executors 50
   --conf spark.executor.extraJavaOptions="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp" --conf spark.serializer=org.apache.spark.serializer.KryoSerializer</spark-opts>
```

### Running

The Spark example can be run as:

`o2a -i examples/spark -o output/spark`


### Output
In this example the output will be created in the `./output/spark/` folder.


## Sqoop Example

### Prerequisites

Make sure to first edit
`configuration.properties` and fill in with configuration data.

Modify the `job.properties` to reflect the correct location of scripts.


### Running

The Sqoop example can be run as:

`o2a -i examples/sqoop -o output/sqoop -x 0.5`

The provided workflow example uses schema 0.5 .

### Output
In this example the output will be created in the `./output/java/` folder.

## Java Example

### Prerequisites

Make sure to first edit
`configuration.properties` and fill in with configuration data.

Modify the `job.properties` to reflect the correct location of scripts.
Copy the lib/demo-java-main.jar to S3 location of choice.

### Running

The Java example can be run as:

`o2a -i examples/java -o output/java -x 0.5`

The provided workflow example uses schema 0.5 .

### Output
In this example the output will be created in the `./output/java/` folder.

## Pig/Hive Example

### Prerequisites

Make sure to first copy `/examples/pig_hive/configuration.template.properties`, rename it as
`configuration.properties` and fill in with configuration data.

Modify the `job.properties` to reflect the correct location of scripts.
ex:

```properties
    pig_script=s3://pinwheel-dipankar/dags/pig_hive/samples/pig-apache/do-reports2.pig
```

### Running

The Pig/Hive example can be run as:

`o2a -i examples/pig_hive -o output/pig_hive`


### Output
In this example the output will be created in the `./output/pig_hive/` folder.


## Sub Workflow Example

### Prerequisites

Make sure to first copy `/examples/subwf/configuration.template.properties`, rename it as
`configuration.properties` and fill in with configuration data.

This workflow calls the pig_hive dag as sub workflow.

### Running

The Pig/Hive example can be run as:

`o2a -i examples/subwf -o output/subwf`


### Output
In this example the output will be created in the `./output/subwf/` folder.

## Coordinator Example

### Prerequisites
Currently Configuration/Property extraction from coordinator is only supported. Dataset dependencies is work in progress.

Keep coordinator file in example folder (same as other example):
```
examples/coord/
├── configuration.properties
├── hdfs
│   ├── coordinator.xml
│   └── workflow.xml
└── job.properties
```
Fill `configuration.properties` with configuration data.

 `job.properties` contains only one parameter `examplesRoot=examples`

### Running

The coordinator example can be run as:

`o2a -i examples/coord/ -o output/coord_demo -n coord_demo_dag`

### Output
In this example the output will be created in the `./output/coord_demo/` folder.

Configuration/Properties from cooridnator is added in DAG at `JOB_PROPS`

#### Note
Pass -x if you want to validate and run the utility for older all schema version. Version 0.4 has been provided.
`o2a -i examples/order_header_item_stage -o output/order_header_item_stage -x 0.4`

# Deployment Instructions
Once the utility has been executed ,locate the generated dag.
Create a zip (dg.zip) by including the follwing
1. o2a directory
2. Generated dag.py file

```
drwxr-xr-x@ 15 dgghosal  staff     480 Oct 21 18:25 o2a
-rw-r--r--   1 dgghosal  staff    4542 Oct 28 13:05 hive.py
-rw-r--r--   1 dgghosal  staff  290618 Oct 28 13:06 dag.zip

```
3.Copy the dag.zip to the dag folder in your Airflow installation if you are running on EC2 using [Packaged DAG](https://airflow.apache.org/docs/stable/concepts.html#packaged-dags)
4. Copy the generated dag.py to dags folder in MWAA along with folders and files below
```
<airflow-bucket/dags>/
             |- .airflowignore        - contains .o2a to be ignored
             |- o2a        - Utility Library
             |- dag.py          - generated dag after running the converter
```

## Bundle Parser
Please refer [bundle-example](examples/bundle) for detail instructions
