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



def write_bytes_to_gcs(bucket_name, blob_name, video_bytes):
    """Writes a video that is loaded in bytes to a blob in the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"
    # video_bytes = "bytes-representing-your-video"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_string(video_bytes)

    print(
        f"Video uploaded to gs://{bucket_name}/{blob_name}."
    )
