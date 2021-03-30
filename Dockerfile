FROM quay.io/astronomer/ap-airflow:2.0.0-3-buster-onbuild

RUN pip install --user boc-0.1-py3-none-any.whl
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True