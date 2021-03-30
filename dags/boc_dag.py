from collections import defaultdict

from pathlib import Path

from airflow import DAG
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.version import version
from datetime import datetime, timedelta

from kedro.framework.session import KedroSession
from kedro.framework.project import configure_project

from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator



class KedroOperator(BaseOperator):

    @apply_defaults
    def __init__(
        self,
        package_name: str,
        pipeline_name: str,
        node_name: str,
        project_path: str,
        env: str,
        *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.package_name = package_name
        self.pipeline_name = pipeline_name
        self.node_name = node_name
        self.project_path = project_path
        self.env = env

    def execute(self, context):
        configure_project(self.package_name)
        with KedroSession.create(self.package_name,
                                 self.project_path,
                                 env=self.env) as session:
            session.run(self.pipeline_name, node_names=[self.node_name])

# Kedro settings required to run your pipeline
env = "local"
pipeline_name = "__default__"
project_path = Path.cwd()
package_name = "boc"

#Define Great Expectations file paths
data_file = '/usr/local/airflow/data/01_raw/iris.csv'
ge_root_dir = '/usr/local/airflow/include/great_expectations'


# Default settings applied to all tasks
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Using a DAG context manager, you don't have to specify the dag property of each task
with DAG(
    "boc",
    start_date=datetime(2019, 1, 1),
    max_active_runs=3,
    schedule_interval=timedelta(minutes=30),  # https://airflow.apache.org/docs/stable/scheduler.html#dag-runs
    default_args=default_args,
    catchup=False # enable if you don't want historical dag runs to run
) as dag:

    ge_batch_kwargs_pass = GreatExpectationsOperator(
        task_id='ge_checkpoint',
        expectation_suite_name='kedro.demo',
        batch_kwargs={
            'path': data_file,
            'datasource': 'data__dir'
        },
        data_context_root_dir=ge_root_dir
    )

    tasks = {}

    tasks["split"] = KedroOperator(
        task_id="split",
        package_name=package_name,
        pipeline_name=pipeline_name,
        node_name="split",
        project_path=project_path,
        env=env,
    )

    tasks["train"] = KedroOperator(
        task_id="train",
        package_name=package_name,
        pipeline_name=pipeline_name,
        node_name="train",
        project_path=project_path,
        env=env,
    )

    tasks["predict"] = KedroOperator(
        task_id="predict",
        package_name=package_name,
        pipeline_name=pipeline_name,
        node_name="predict",
        project_path=project_path,
        env=env,
    )

    tasks["report"] = KedroOperator(
        task_id="report",
        package_name=package_name,
        pipeline_name=pipeline_name,
        node_name="report",
        project_path=project_path,
        env=env,
    )

    ge_batch_kwargs_pass >> tasks["split"]

    tasks["split"] >> tasks["train"]

    tasks["split"] >> tasks["report"]

    tasks["split"] >> tasks["predict"]

    tasks["predict"] >> tasks["report"]

    tasks["train"] >> tasks["predict"]
