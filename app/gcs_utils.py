from google.cloud import storage

def upload_to_gcs(file_obj, bucket_name, dest_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(dest_blob_name)
    blob.upload_from_file(file_obj, content_type="audio/mp3")
    return f"gs://{bucket_name}/{dest_blob_name}"
