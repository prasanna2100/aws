from airflow import DAG
from airflow.providers.amazon.aws.operators.lambda_function import AwsLambdaInvokeFunctionOperator
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=3)
}

dag = DAG(
    'dynamodb_to_redshift_simple_pipeline',
    default_args=default_args,
    start_date=datetime(2024, 2, 10),
    schedule_interval='@daily',
    catchup=False
)

# Single Lambda to Check & Export
check_and_export = AwsLambdaInvokeFunctionOperator(
    task_id='check_and_export_to_s3',
    function_name='check_and_export_lambda',
    aws_conn_id='aws_default',
    invocation_type='RequestResponse',
    payload=json.dumps({"action": "check_and_export"}),
    log_type='Tail',
    dag=dag
)

# Copy Data from S3 to Redshift
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator

load_to_redshift = S3ToRedshiftOperator(
    task_id='load_s3_to_redshift',
    aws_conn_id='aws_default',
    s3_bucket='my-bucket',
    s3_key='exports/prescription_data.parquet',
    schema='public',
    table='prescription',
    copy_options=['FORMAT AS PARQUET'],
    redshift_conn_id='redshift_default',
    dag=dag
)

# DAG Dependency
check_and_export >> load_to_redshift
