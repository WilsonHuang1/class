import json
import boto3
import os
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        # Get the S3 bucket and file information from the event
        bucket = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        
        # Get file metadata from S3
        response = s3_client.head_object(
            Bucket=bucket,
            Key=file_key
        )
        
        # Extract metadata
        file_size = response['ContentLength']
        etag = response['ETag'].strip('"')  # Remove quotes from ETag
        upload_date = datetime.now().isoformat()
        bucket_arn = f"arn:aws:s3:::{bucket}"
        file_arn = f"{bucket_arn}/{file_key}"
        
        # Prepare item for DynamoDB
        item = {
            'fileName': file_key,
            'uploadDate': upload_date,
            'fileSize': file_size,
            'fileArn': file_arn,
            'eTag': etag,
            'bucket': bucket
        }
        
        # Log the metadata to CloudWatch
        logger.info('File metadata:')
        logger.info(json.dumps(item, indent=2))
        
        # Write to DynamoDB
        table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'hw04-files'))
        table.put_item(Item=item)
        
        logger.info('Successfully wrote metadata to DynamoDB')
        
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully processed file upload')
        }
        
    except Exception as e:
        logger.error(f'Error processing file: {str(e)}')
        raise e