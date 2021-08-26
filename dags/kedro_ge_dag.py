from airflow import DAG
from airflow.version import version
from datetime import datetime, timedelta
from plugins.operators.kedro_operator import KedroOperator
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
from pathlib import Path

# Kedro settings required to run your pipeline
env = "local"
pipeline_name = "__default__"
project_path = Path.cwd()
package_name = "boc"

#Define Great Expectations file paths
raw_data_file = '/usr/local/airflow/data/01_raw/iris.csv'
test_data_file = '/usr/local/airflow/data/05_model_input/example_test_x.pkl'
train_data_file = '/usr/local/airflow/data/05_model_input/example_train_x.pkl'
ge_root_dir = '/usr/local/airflow/include/great_expectations'


with DAG("kedro-ge",
        start_date=datetime(2021, 1, 1),
        max_active_runs=1,
        schedule_interval='@daily',
        default_args={
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 1,
            'retry_delay': timedelta(minutes=1),
        },
        catchup=False
    ) as dag:

    ge_raw_checkpoint = GreatExpectationsOperator(
        task_id='ge_raw_checkpoint',
        expectation_suite_name='kedro.raw',
        batch_kwargs={
            'path': raw_data_file,
            'datasource': 'data__dir'
        },
        data_context_root_dir=ge_root_dir
    )

    ge_train_checkpoint = GreatExpectationsOperator(
        task_id='ge_train_checkpoint',
        expectation_suite_name='kedro.train',
        batch_kwargs={
            'path': train_data_file,
            'datasource': 'data__dir'
        },
        data_context_root_dir=ge_root_dir
    )

    ge_test_checkpoint = GreatExpectationsOperator(
        task_id='ge_test_checkpoint',
        expectation_suite_name='kedro.test',
        batch_kwargs={
            'path': test_data_file,
            'datasource': 'data__dir'
        },
        data_context_root_dir=ge_root_dir
    )

    kedro_split = KedroOperator(
        task_id="split",
        package_name=package_name,
        pipeline_name=pipeline_name,
        node_name="split",
        project_path=project_path,
        env=env,
    )

    kedro_train = KedroOperator(
        task_id="train",
        package_name=package_name,
        pipeline_name=pipeline_name,
        node_name="train",
        project_path=project_path,
        env=env,
    )

    kedro_predict = KedroOperator(
        task_id="predict",
        package_name=package_name,
        pipeline_name=pipeline_name,
        node_name="predict",
        project_path=project_path,
        env=env,
    )

    kedro_report = KedroOperator(
        task_id="report",
        package_name=package_name,
        pipeline_name=pipeline_name,
        node_name="report",
        project_path=project_path,
        env=env,
    )

    ge_raw_checkpoint >> kedro_split >> kedro_train >> ge_train_checkpoint >> kedro_predict >> kedro_report
    kedro_split >> ge_test_checkpoint >> kedro_predict
    kedro_split >> kedro_report
