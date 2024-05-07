from google.cloud import storage


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