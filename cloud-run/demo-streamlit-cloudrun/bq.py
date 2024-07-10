from tenacity import retry, stop_after_attempt, wait_random_exponential

#TODO: retry if pandas_gbq.exceptions.GenericGBQException  Reason: 403 Exceeded rate limits

@retry(wait=wait_random_exponential(min=10, max=60), stop=stop_after_attempt(10) )
def save_bq(df, table_id, project_id, cast_as_str = True):
    import pandas
    import pandas_gbq

    print(f"save_bq  {table_id} {project_id}")

    # check if dataframe is empty
    if df is None or df.empty:
        print("empty dataframe")
        return
    
    if cast_as_str == True:
        df = df.astype(str)
        print(df.to_json(orient='records'))

    pandas_gbq.to_gbq(df, table_id, project_id=project_id , if_exists='append', verbose= True)

def save_unsafe_bq(df, table_id, project_id, cast_as_str = True):
    import pandas
    import pandas_gbq

    print(f"save_bq  {table_id} {project_id}")

    # check if dataframe is empty
    if df is None or df.empty:
        print("empty dataframe")
        return
    
    if cast_as_str == True:
        df = df.astype(str)
        print(df.to_json(orient='records'))

    pandas_gbq.to_gbq(df, table_id, project_id=project_id , if_exists='append', verbose= True)


# @title Setup
from google.cloud import bigquery
import config as config

client = bigquery.Client(project=config.PROJECT_ID, location=config.REGION)
#print(f"project = {client.project} - _credentials = {client._credentials.to_json()}" )


@retry(wait=wait_random_exponential(min=10, max=60), stop=stop_after_attempt(10) )
def save_embeddings_df_bq(df, table_id, truncate = False):
    job_config = bigquery.LoadJobConfig(
    # Specify a (partial) schema. All columns are always written to the
    # table. The schema is used to assist in data type definitions.
    schema=[

bigquery.SchemaField("video_source", "STRING")	,
bigquery.SchemaField("description", "STRING")	,

bigquery.SchemaField("embeddings", bigquery.enums.SqlTypeNames.FLOAT, mode="REPEATED"),
#bigquery.SchemaField("index","int", mode="NULLABLE"),	

bigquery.SchemaField("start","FLOAT", mode="NULLABLE"),	
bigquery.SchemaField("stop","FLOAT", mode="NULLABLE"),	
bigquery.SchemaField("MODEL_MULTIMODAL", "STRING")	,

    ],
    # Optionally, set the write disposition. BigQuery appends loaded rows
    # to an existing table by default, but with WRITE_TRUNCATE write
    # disposition it replaces the table with the loaded data.
    #write_disposition="WRITE_TRUNCATE",
    
    )
    if truncate:
        print('truncate table: ' + table_id)
        job_config.write_disposition="WRITE_TRUNCATE"

    job = client.load_table_from_dataframe(
        df, table_id, job_config=job_config
    )  # Make an API request.
    job.result()  # Wait for the job to complete.



def save_results_df_bq(df, table_id, truncate = False):
    job_config = bigquery.LoadJobConfig(
    # Specify a (partial) schema. All columns are always written to the
    # table. The schema is used to assist in data type definitions.


    schema=[

bigquery.SchemaField("index", bigquery.enums.SqlTypeNames.int )	,
bigquery.SchemaField("time_start","FLOAT", mode="NULLABLE"),	
bigquery.SchemaField("time_stop","FLOAT", mode="NULLABLE"),	
bigquery.SchemaField("video_blobname","STRING", mode="NULLABLE"),	
bigquery.SchemaField("video_source","STRING", mode="NULLABLE"),	
bigquery.SchemaField("description","STRING", mode="NULLABLE"),	
bigquery.SchemaField("update_time","STRING", mode="NULLABLE"),	
bigquery.SchemaField("uri","STRING", mode="NULLABLE"),	



    ],
    # Optionally, set the write disposition. BigQuery appends loaded rows
    # to an existing table by default, but with WRITE_TRUNCATE write
    # disposition it replaces the table with the loaded data.
    #write_disposition="WRITE_TRUNCATE",
    
    )
    if truncate:
        print('truncate table: ' + table_id)
        job_config.write_disposition="WRITE_TRUNCATE"

    job = client.load_table_from_dataframe(
        df, table_id, job_config=job_config
    )  # Make an API request.
    job.result()  # Wait for the job to complete.


def query(query):

    print(query)
    print("PROJECT_ID = " + config.PROJECT_ID)
    queryJob = client.query(query, project=config.PROJECT_ID, location=config.BQ_REGION)
    result = queryJob.result()

    df = result.to_dataframe()
    return df