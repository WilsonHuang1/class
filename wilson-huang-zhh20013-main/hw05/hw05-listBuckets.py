import boto3
import json
import logging

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def list_buckets_function(event, context):
    # Log incoming event data
    logger.info(f"Event received in list_buckets_function: {json.dumps(event)}")
    
    try:
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        logger.info(f"Successfully retrieved {len(buckets)} buckets")
        
        return {
            'statusCode': 200,
            'body': json.dumps(buckets)
        }
    except Exception as e:
        logger.error(f"Error listing buckets: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }