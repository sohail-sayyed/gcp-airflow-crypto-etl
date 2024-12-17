from airflow import DAG
from datetime import datetime
import json
import requests
import pandas as pd
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator, BigQueryCreateEmptyTableOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.contrib.operators.bigquery_table_delete_operator import BigQueryTableDeleteOperator


# Global Variables
BUCKET_NAME = 'airflow-bucket-sohail'
GCP_CONN_ID = 'google_cloud_default'
RAW_FILE_NAME = 'crypto_data.json'
RAW_FILE_DEST = 'raw_data/crypto_coins/'
TRANSFORMED_FILE_NAME = 'crypto_details.csv'
TRANSFORMED_FILE_DEST = 'transformed_data/crypto_coins/'
PROJECT_ID = 'learn-airflow-442814'
DATASET_ID = 'crypto_dataset'
TABLE_NAME = 'crypto_table'
BQ_SCHEMA = [
    {"name": "coin_name", "type": "STRING", "mode": "REQUIRED"},
    {"name": "coin_id", "type": "INTEGER", "mode": "REQUIRED"},
    {"name": "price_btc", "type": "FLOAT", "mode": "REQUIRED"},
    {"name": "market_cap_usd", "type": "INTEGER", "mode": "REQUIRED"},
    {"name": "bitcoin_description", "type": "STRING", "mode": "REQUIRED"}
]




default_args = {
    'owner': 'sohail_sayyed',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': 60,
}


dag = DAG(
    dag_id='crypto_coins_airflow_gcp',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['crypto_coins'],
    description='Making an API call to crypto coins API and fetching the trending data of crypto coins.'
)

def _get_crypto_coins(**kwargs):
    """
    Task to fetch data from coingecko API.

    Makes an API call to coingecko API and fetches the trending data of crypto coins.
    The API call is made with accept header set to application/json.
    The result of the API call is then written to a file named crypto_data.json
    in the current working directory.

    Args:
        **kwargs: Arbitrary keyword arguments.

    Returns:
        None
    """
    headers = {"accept": "application/json"}
    url ='https://api.coingecko.com/api/v3/search/trending'
    response = requests.get(url, headers=headers)

    with open('crypto_data.json', 'w') as f:
        json.dump(response.json(), f)


def _transform_crypto_data(**kwargs):
    """
    Task to transform the raw crypto data into a structured format.

    This task takes the raw crypto data fetched from the API and transforms it into a structured format using pandas dataframe.
    The dataframe is then saved as a csv file named crypto_details.csv in the current working directory.

    Args:
        **kwargs: Arbitrary keyword arguments.

    Returns:
        None
    """
    with open('crypto_data.json', 'r') as f:
        response_json = json.load(f)
    
    coins_info = []
    for i in response_json['coins']:
        coin_id = i['item'].get('coin_id', 'N/A')
        coin_name = i['item'].get('name', 'N/A')
        price_btc = i['item'].get('data', {}).get('price_btc', 'N/A')
        market_cap = i['item'].get('data', {}).get('market_cap', 'N/A')
        content = i['item']['data'].get('content', {})
        if content:
            bitcoin_description = content.get('description', 'No description available')
        else:
            bitcoin_description = None
        coins_info.append({'coin_name': coin_name, 'coin_id': coin_id, 'price_btc': price_btc, 'market_cap': market_cap, 'bitcoin_description': bitcoin_description})

    crypto_df = pd.DataFrame(coins_info)
    crypto_df['market_cap'] = crypto_df['market_cap'].str.replace('[$,]', '', regex=True)
    crypto_df[['price_btc', 'market_cap']] = crypto_df[['price_btc', 'market_cap']].apply(pd.to_numeric)
    crypto_df.rename(columns={'market_cap': 'market_cap_usd'}, inplace=True)

    crypto_df.to_csv('crypto_details.csv', index=False)

# Fetching Crypto Data
fetch_crypto_data = PythonOperator(
    task_id='fetch_crypto_data',
    python_callable=_get_crypto_coins,
    dag=dag
)

# Creating GCS Bucket
create_bucket = GCSCreateBucketOperator(
    task_id='creating_gcs_bucket',
    bucket_name=BUCKET_NAME,
    gcp_conn_id=GCP_CONN_ID,
    dag=dag
)


# Uploading Raw Crypto Data from Local to GCS
upload_raw_crypto_data_to_gcs = LocalFilesystemToGCSOperator(
    task_id='uploading_raw_crypto_data_to_gcs',
    src=RAW_FILE_NAME,
    dst=RAW_FILE_DEST,
    bucket=BUCKET_NAME,
    gcp_conn_id=GCP_CONN_ID,
    dag=dag
)


# Transforming Crypto Data 
transformed_data = PythonOperator(
    task_id='transforming_crypto_data',
    python_callable=_transform_crypto_data,
    dag=dag
)


# Uploading Transformed Crypto Data to GCS
upload_transformed_crypto_data_to_gcs = LocalFilesystemToGCSOperator(
    task_id='upload_transformed_crypto_data_to_gcs',
    src=TRANSFORMED_FILE_NAME,
    dst=TRANSFORMED_FILE_DEST,
    bucket=BUCKET_NAME,
    gcp_conn_id=GCP_CONN_ID,
    dag=dag
)


# Creating BigQuery Dataset
create_dataset_bigquery = BigQueryCreateEmptyDatasetOperator(
    task_id='creating_bigquery_dataset',
    dataset_id=DATASET_ID,
    gcp_conn_id=GCP_CONN_ID,
    dag=dag
)


# Creating BigQuery Table
create_table_bigquery = BigQueryCreateEmptyTableOperator(
    task_id='creating_bigquery_table',
    dataset_id=DATASET_ID,
    table_id=TABLE_NAME,
    schema_fields=BQ_SCHEMA,
    gcp_conn_id=GCP_CONN_ID,
    dag=dag
)


# Uploading Data to BigQuery
upload_data_to_bq = GCSToBigQueryOperator(
    task_id='uploading_data_to_bq',
    bucket=BUCKET_NAME,
    source_objects=TRANSFORMED_FILE_DEST + TRANSFORMED_FILE_NAME,
    destination_project_dataset_table=f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}",
    source_format='CSV',
    gcp_conn_id=GCP_CONN_ID,
    write_disposition='WRITE_APPEND',
    skip_leading_rows=1,
    force_delete=True,
    dag=dag
)

# For deleting Dataset
# delete_table = BigQueryTableDeleteOperator(
#     task_id='deleting_table',
#     # dataset_id=DATASET_ID,
#     deletion_dataset_table=f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}",
#     gcp_conn_id=GCP_CONN_ID,
#     dag=dag
# )


fetch_crypto_data >> create_bucket >> upload_raw_crypto_data_to_gcs >> transformed_data >>  upload_transformed_crypto_data_to_gcs
upload_transformed_crypto_data_to_gcs >> create_dataset_bigquery >> create_table_bigquery >> upload_data_to_bq
# delete_table
