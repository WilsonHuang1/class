import json
import boto3
import urllib.parse
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event))
    
    # Get the target bucket for thumbnails
    thumbnail_bucket = os.environ.get('THUMBNAIL_BUCKET')
    if not thumbnail_bucket:
        logger.error("THUMBNAIL_BUCKET environment variable not set")
        return {'statusCode': 500, 'body': 'Configuration error: THUMBNAIL_BUCKET not set'}
    
    for record in event['Records']:
        try:
            # Parse the message from SNS via SQS
            message = json.loads(record['body'])
            s3_event = json.loads(message['Message'])
            
            for s3_record in s3_event['Records']:
                # Extract source bucket and key
                source_bucket = s3_record['s3']['bucket']['name']
                object_key = s3_record['s3']['object']['key']
                
                # Get file size from the event
                file_size = s3_record['s3']['object']['size']
                
                # URL decode the key
                decoded_key = urllib.parse.unquote_plus(object_key)
                logger.info(f"Processing image: {decoded_key} from bucket {source_bucket}")
                logger.info(f"File size: {file_size} bytes")
                
                # EXTRA CREDIT: Raise exception if file is over 100KB
                if file_size > 100000:  # 100KB in bytes
                    error_msg = f"File size {file_size} bytes exceeds the 100KB limit"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                # Only process image files
                if not (decoded_key.lower().endswith('.jpg') or 
                       decoded_key.lower().endswith('.jpeg') or 
                       decoded_key.lower().endswith('.png')):
                    logger.info(f"Skipping non-image file: {decoded_key}")
                    continue
                
                try:
                    # Create thumbnail filename
                    filename, file_extension = os.path.splitext(decoded_key)
                    thumbnail_key = f"{filename}_thumbnail{file_extension}"
                    
                    # Create a text file as a placeholder thumbnail
                    content = f"This is a thumbnail placeholder for {decoded_key}"
                    
                    # Upload the placeholder to the thumbnail bucket
                    s3_client.put_object(
                        Bucket=thumbnail_bucket,
                        Key=thumbnail_key,
                        Body=content,
                        ContentType='text/plain'
                    )
                    
                    logger.info(f"Successfully created placeholder thumbnail: {thumbnail_key} in bucket {thumbnail_bucket}")
                    
                except Exception as e:
                    logger.error(f"Error processing {decoded_key}: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    raise  # Re-raise to send to DLQ after max retries
        
        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise  # Re-raise to send to DLQ after max retries
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }