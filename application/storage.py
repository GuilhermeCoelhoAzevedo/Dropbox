from application import storage_client, bucket
import local_constants

def blobList(prefix, delimiter=None):    
    return storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=prefix, delimiter=delimiter)

def addDirectory(directory_name):
    blob = bucket.blob(directory_name)
    blob.upload_from_string('', content_type='application/x-www-formurlencoded;charset=UTF-8')

def addFile(path, file):
    blob = bucket.blob(path + file.filename)
    blob.upload_from_file(file)

def delete_blob(blob_name):    
    blobs = bucket.list_blobs(prefix=blob_name)

    for blob in blobs:
        blob.delete()

def downloadBlob(filename):
    blob = bucket.blob(filename)
 
    return blob.download_as_bytes()