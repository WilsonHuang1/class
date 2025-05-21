import boto3
import json
import logging
import base64

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def add_object_function(event, context):
    # Log incoming event data
    logger.info(f"Event received in add_object_function: {json.dumps(event)}")
    
    try:
        # Extract bucket name from path parameters
        bucket_name = event['pathParameters']['bucket-name']
        logger.info(f"Target bucket: {bucket_name}")
        
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body'])
            object_name = body.get('name')
            content = body.get('content')
            
            logger.info(f"Object name: {object_name}")
            logger.info(f"Content length: {len(content) if content else 0} characters")
            
            if not object_name or not content:
                logger.warning("Missing required parameters: object name or content")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Object name and content are required'})
                }
            
            s3 = boto3.client('s3')
            s3.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=content
            )
            
            logger.info(f"Successfully uploaded object {object_name} to bucket {bucket_name}")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': f'Object {object_name} created successfully'})
            }
        else:
            logger.warning("Request body is missing")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Request body is missing'})
            }
    except Exception as e:
        logger.error(f"Error adding object to bucket {bucket_name if 'bucket_name' in locals() else 'unknown'}: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
}   
    