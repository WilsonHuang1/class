import boto3
from botocore.exceptions import ClientError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3Resource:
    def __init__(self, bucket_name):
        """
        Initialize S3 resource with specified bucket
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')
        logger.info(f"Initialized S3Resource with bucket: {bucket_name}")

    def list_objects(self):
        """
        List all objects in the bucket with their details
        Returns a list of dictionaries with object information
        """
        try:
            logger.info(f"Listing objects in bucket: {self.bucket_name}")
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            if 'Contents' not in response:
                logger.info("No objects found in bucket")
                return []
            
            objects = []
            for obj in response['Contents']:
                objects.append({
                    'Name': obj['Key'],
                    'Size': obj['Size'],
                    'LastModified': obj['LastModified'].isoformat()
                })
            
            logger.info(f"Found {len(objects)} objects in bucket")
            return objects
        except ClientError as e:
            logger.error(f"Error listing objects: {e}")
            return []

    def list_buckets(self):
        """
        List all buckets in the account
        """
        try:
            logger.info("Listing all buckets")
            response = self.s3_client.list_buckets()
            
            if 'Buckets' not in response:
                logger.info("No buckets found")
                return []
            
            buckets = []
            for bucket in response['Buckets']:
                buckets.append({
                    'Name': bucket['Name'],
                    'CreationDate': bucket['CreationDate'].isoformat()
                })
            
            logger.info(f"Found {len(buckets)} buckets")
            return buckets
        except ClientError as e:
            logger.error(f"Error listing buckets: {e}")
            return []

    def set_bucket(self, bucket_name):
        """
        Change the current bucket
        """
        logger.info(f"Changing bucket from {self.bucket_name} to {bucket_name}")
        self.bucket_name = bucket_name
        return True

    # Make sure method name matches what's called in routes.py
    def upload_file_to_s3(self, file_obj, filename):
        """
        Upload a file to the S3 bucket
        """
        try:
            logger.info(f"Uploading file {filename} to bucket {self.bucket_name}")
            self.s3_client.upload_fileobj(file_obj, self.bucket_name, filename)
            logger.info(f"Successfully uploaded {filename}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading file: {e}")
            return False

    def generate_presigned_url(self, object_key, expiration=3600):
        """
        Generate a presigned URL for accessing an object
        """
        try:
            logger.info(f"Generating presigned URL for {object_key}")
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None
        
    def delete_object(self, object_key):
        """
        Delete an object from the S3 bucket
        """
        try:
            logger.info(f"Deleting object {object_key} from bucket {self.bucket_name}")
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            logger.info(f"Successfully deleted {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting object: {e}")
            return False