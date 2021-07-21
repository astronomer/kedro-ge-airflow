# Airflow + Kedro + Great Expectations Demo

## Overview

This project shows how to use three open source tools, Airflow, Kedro, and Great Expectations, together to help productionize machine learning pipelines. It was developed to support a talk on this topic given at the 2021 Airflow Summit. You can find a recording of the talk [here](https://airflowsummit.org/live/). 

The repo contains two example DAGs:
 - `kedro_raw.py` is a DAG created automatically from a Kedro project (more on this in the Kedro section below)
 - `kedro_ge_dag.py` is a DAG that integrates Great Expectations checks into a Kedro pipeline

The repo also contains supporting file structure for the Kedro project and the Great Expectations validations as described below. 

## Repo Structure
This repo contains two example DAGs, as well as supporting files for Kedro and Great Expectations. The file structure is a combination of an Astronomer Airflow project, and a `kedro-airflow` project. Below are high level descriptions of each folder as a guide:

```
+-- conf/                     # Kedro project configuration files generated automatically by `kedro-airflow`
+-- dags/                     # Airflow DAGs 
+-- data/                     # Data used for Kedro project, in this case the Iris dataset
+-- include/
|   +-- great_expectations/   # Great Expectations supporting files, including checkpoints and expectations
+-- plugins/
|   +-- operators/            # Custom operators, in this case the `KedroOperator` generated automatically by `kedro-airflow`
+-- src/                      # Source for the Kedro package, including all Kedro node and pipeline code that is used by the `KedroOperator` tasks
```

## Kedro
[Kedro](https://github.com/quantumblacklabs/kedro) is an open source development workflow tool that helps structure reproducible, scaleable, deployable, robust and versioned machine learning data pipelines. You can read more about the project [here](https://kedro.readthedocs.io/en/0.15.3/01_introduction/01_introduction.html).

Once you have a Kedro project, you can turn it into an Airflow DAG using the `kedro-airflow` package. Documentation on the package and how to use it can be found [here](https://github.com/quantumblacklabs/kedro-airflow). 

This repo uses the [Iris example project](https://kedro.readthedocs.io/en/stable/02_get_started/05_example_project.html) from Kedro to convert into an Airflow DAG with simple split, train, predict, and report steps.


## Great Expectations
[Great Expectations](https://greatexpectations.io/) is an open source Python framework for data validations. In the context of an Airflow DAG, it can be used to implement data validation checks at any point in your pipeline. This repo makes use of the [Great Expectations provider package](https://registry.astronomer.io/providers/great-expectations), which can be used to easily implement checks using the `GreatExpectationsOperator`.


## Getting Started

The easiest way to run these example DAGs is to use the Astronomer CLI to get an Airflow instance up and running locally:

 1. [Install the Astronomer CLI](https://www.astronomer.io/docs/cloud/stable/develop/cli-quickstart)
 2. Clone this repo somewhere locally and navigate to it in your terminal
 3. Initialize an Astronomer project by running `astro dev init`
 4. Start Airflow locally by running `astro dev start`
 5. Navigate to localhost:8080 in your browser and you should see the tutorial DAGs there
