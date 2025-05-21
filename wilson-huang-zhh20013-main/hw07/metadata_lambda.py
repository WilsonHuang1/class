import boto3
import json
import logging
import os
from datetime import datetime
import urllib.parse

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Process SQS messages to store metadata for uploaded images
    """
    logger.info("Received event: " + json.dumps(event))
    
    # Get the target DynamoDB table
    table_name = os.environ.get('METADATA_TABLE', 'hw07-image-metadata')
    table = dynamodb.Table(table_name)
    
    for record in event['Records']:
        try:
            # Parse the message from SNS via SQS
            message = json.loads(record['body'])
            
            # The SNS message contains the S3 event
            s3_event = json.loads(message['Message'])
            
            for s3_record in s3_event['Records']:
                # Extract bucket and key
                bucket = s3_record['s3']['bucket']['name']
                object_key = s3_record['s3']['object']['key']
                
                # URL decode the key (important for files with special characters)
                decoded_key = urllib.parse.unquote_plus(object_key)
                logger.info(f"Processing object: {decoded_key} in bucket {bucket}")
                
                # Get data from the S3 event rather than making an additional call
                try:
                    size = s3_record['s3']['object']['size']
                    etag = s3_record['s3']['object']['eTag'].strip('"')
                    
                    # Store in DynamoDB
                    item = {
                        'ObjectName': decoded_key,       # Use decoded name for readability
                        'ObjectKey': object_key,         # Store original key for reference
                        'Bucket': bucket,
                        'Size': size,
                        'LastModified': datetime.now().isoformat(),
                        'ETag': etag,
                        'Timestamp': datetime.now().isoformat()
                    }
                    
                    table.put_item(Item=item)
                    logger.info(f"Successfully stored metadata for {decoded_key}")
                    
                except Exception as e:
                    logger.error(f"Error processing metadata for {object_key}: {str(e)}")
                    # Log the full stacktrace
                    import traceback
                    logger.error(traceback.format_exc())
        
        except Exception as e:
            logger.error(f"Error processing SQS message: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    return {
        'statusCode': 200,
        'body': json.dumps('Metadata storage completed')
    }