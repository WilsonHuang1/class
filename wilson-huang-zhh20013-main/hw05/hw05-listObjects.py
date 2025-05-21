import boto3
import json
import logging

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def list_objects_function(event, context):
    # Log incoming event data
    logger.info(f"Event received in list_objects_function: {json.dumps(event)}")
    
    try:
        # Extract bucket name from path parameters
        bucket_name = event['pathParameters']['bucket-name']
        logger.info(f"Requested bucket name: {bucket_name}")
        
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        # If the bucket exists but has no objects
        if 'Contents' not in response:
            logger.info(f"Bucket {bucket_name} exists but has no objects")
            objects = []
        else:
            objects = [obj['Key'] for obj in response['Contents']]
            logger.info(f"Retrieved {len(objects)} objects from bucket {bucket_name}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(objects)
        }
    except Exception as e:
        logger.error(f"Error listing objects from bucket {bucket_name if 'bucket_name' in locals() else 'unknown'}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }