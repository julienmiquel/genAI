from google.cloud import storage


def exist(bucket_name, file_name):
    """Writes the input to a file in the specified bucket.

    Args:
    bucket_name: The name of the bucket to write to.
    file_name: The name of the file to write to.
    input: The input to write to the file.

    Returns:
    The name of the file that was written to.
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    return blob.exists

def write_string_to_bucket(bucket_name, file_name, input):
    """Writes the input to a file in the specified bucket.

    Args:
    bucket_name: The name of the bucket to write to.
    file_name: The name of the file to write to.
    input: The input to write to the file.

    Returns:
    The name of the file that was written to.
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    blob.upload_from_string(input)

    return blob.name



def write_bytes_to_gcs(bucket_name, blob_name, video_bytes, content_type='video/mp4'):
    """Writes a video that is loaded in bytes to a blob in the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"
    # video_bytes = "bytes-representing-your-video"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_string(video_bytes, content_type=content_type)

    print(
        f"Video uploaded to gs://{bucket_name}/{blob_name}."
    )
    return f"gs://{bucket_name}/{blob_name}"


def write_file_to_gcs(gcs_bucket_name,  gcs_file_name, local_file_path, tags = None):
    """Writes a local file to GCS.

    Args:
    local_file_path: The path to the local file to write to GCS.
    gcs_bucket_name: The name of the GCS bucket to write the file to.
    gcs_file_name: The name of the GCS file to write the file to.

    Returns:
    The GCS file path.
    """
    print(f"local_file_path = {local_file_path} - gcs_bucket_name = {gcs_bucket_name} - gcs_file_name = {gcs_file_name}")
    storage_client = storage.Client()
    bucket = storage_client.bucket(gcs_bucket_name)
    blob = bucket.blob(gcs_file_name)
    if tags is not None:
        blob.metadata = tags

    print(f"upload_from_filename : local_file_path = {local_file_path}")
    blob.upload_from_filename(local_file_path, ) 

    return blob


def store_temp_video_from_gcs(bucket_name, file_name, localfile):
    import tempfile
    import os

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # try:        
    bytes_data = blob.download_as_bytes()
    
    # Create a temporary file.
    # tempDir = tempfile.gettempdir()
    tempDir = os.getcwd()

    temp_path = os.path.join(tempDir, localfile)
    # f, temp_path = tempfile.mkstemp()
    fp = open(temp_path, 'bw')
    fp.write(bytes_data)
    fp.seek(0)


    return temp_path



import re

def split_gcs_uri(gcs_uri):
  """Splits a GCS URI into bucket name and blob path variables.

  Args:
    gcs_uri: The GCS URI to split.

  Returns:
    A tuple containing the bucket name and blob path.
  """

  match = re.match(r"gs://([^/]+)/(.+)", gcs_uri)
  if match:
    return match.groups()
  else:
    raise ValueError("Invalid GCS URI: {}".format(gcs_uri))

import datetime

from google.cloud import storage
from google.auth import compute_engine
import google.auth

def generate_download_signed_url(uri):
    bucket_name, blob_name = split_gcs_uri(uri)
    return generate_download_signed_url_v4(bucket_name, blob_name)

def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    storage_client = storage.Client.from_service_account_json("/Users/julienmiquel/dev/credentials/ml-demo-384110-83ec709a851a.json")
    storage_client = storage.Client.from_service_account_json("/Users/julienmiquel/dev/vi-dev2/video-intelligence/credentials.json")

    #storage_client = storage.Client(project=config.PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)


    # auth_request = google.auth.transport.requests.Request()
    # credentials, project = google.auth.default()


    # signing_credentials = compute_engine.IDTokenCredentials(
    #     auth_request,
    #     "",
    #     service_account_email=credentials.external_account_id
    # )

    from google.auth.transport import requests
    from google.auth import default, compute_engine, load_credentials_from_file
    
    #credentials = load_credentials_from_file("/Users/julienmiquel/dev/vi-dev2/video-intelligence/credentials.json")
    #credentials, project = default()
    
    # then within your abstraction
    #auth_request = requests.Request()
    #credentials.refresh(auth_request)
    
    # signing_credentials = compute_engine.IDTokenCredentials(
    #     auth_request,
    #     "",
    #     service_account_email=credentials.service_account_email
    # )

    url = blob.generate_signed_url(
        version="v4",
        #credentials=credentials,
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(days=6),
        #expiration=datetime.timedelta(minutes=15),
        
        # Allow GET requests using this URL.
        method="GET",
        
    )

    print("Generated GET signed URL:")
    print(url)
    print("You can use this URL with any user agent, for example:")
    print(f"curl '{url}'")
    return url