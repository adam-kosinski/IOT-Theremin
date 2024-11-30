import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

bucket_name = "ece665recordings--use2-az1--x-s3"

def upload_to_s3(file_name, bucket_name, object_name=None):
    # If no object name is provided, use the file name
    if object_name is None:
        object_name = file_name

    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # Upload the file to the specified S3 bucket
        s3.upload_file(file_name, bucket_name, object_name)
        print(f"File '{file_name}' uploaded to bucket '{bucket_name}' as '{object_name}'")
    except FileNotFoundError:
        print(f"The file '{file_name}' was not found.")
    except NoCredentialsError:
        print("Credentials not available.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")

def list_files_in_bucket(bucket_name):
    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # List the files in the specified S3 bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            print(f"Files in bucket '{bucket_name}':")
            for obj in response['Contents']:
                print(obj['Key'])
            
            return [obj['Key'] for obj in response['Contents']]
        else:
            print(f"Bucket '{bucket_name}' is empty.")
            return []
    except NoCredentialsError:
        print("Credentials not available.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
    except s3.exceptions.NoSuchBucket:
        print(f"Bucket '{bucket_name}' does not exist.")

def get_presigned_url(bucket_name, object_name, expiration=3600):
    # Create an S3 client
    s3 = boto3.client('s3')

    try:
        # Generate a pre-signed URL for the S3 object
        url = s3.generate_presigned_url('get_object',
                                        Params={'Bucket': bucket_name, 'Key': object_name},
                                        ExpiresIn=expiration)
        print(f"Pre-signed URL: {url}")
        return url
    except NoCredentialsError:
        print("Credentials not available.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")

if __name__ == "__main__":
    # Specify the file, bucket, and optionally object name
    file_name = "recording.mp3"
    bucket_name = "ece665recordings--use2-az1--x-s3"
    object_name = file_name

    # Upload the file to S3
    upload_to_s3(file_name, bucket_name)

    # List all files in the bucket
    list_files_in_bucket(bucket_name)

    # Generate a pre-signed URL to stream/download the file
    get_presigned_url(bucket_name, object_name)
