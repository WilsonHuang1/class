import boto3
import json
import logging

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def delete_object_function(event, context):
    # Log incoming event data
    logger.info(f"Event received in delete_object_function: {json.dumps(event)}")
    
    try:
        # Extract bucket and object names from path parameters
        bucket_name = event['pathParameters']['bucket-name']
        object_name = event['pathParameters']['object-name']
        
        logger.info(f"Target bucket: {bucket_name}")
        logger.info(f"Target object: {object_name}")
        
        s3 = boto3.client('s3')
        s3.delete_object(
            Bucket=bucket_name,
            Key=object_name
        )
        
        logger.info(f"Successfully deleted object {object_name} from bucket {bucket_name}")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Object {object_name} deleted successfully from {bucket_name}'})
        }
    except Exception as e:
        logger.error(f"Error deleting object {object_name if 'object_name' in locals() else 'unknown'} from bucket {bucket_name if 'bucket_name' in locals() else 'unknown'}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }