import json
import boto3
import csv
import io
from datetime import datetime

def lambda_handler(event, context):
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3')
        
        # Get bucket name from the event
        bucket = event['Records'][0]['s3']['bucket']['name']
        
        # Get list of all objects in the bucket
        response = s3_client.list_objects_v2(Bucket=bucket)
        
        # Prepare CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['FileName', 'FileSize', 'UploadDate', 'FileARN', 'ETag'])
        
        # Write data for each object
        if 'Contents' in response:
            for obj in response['Contents']:
                # Skip the inventory file itself if it exists
                if obj['Key'] == 'bucket-inventory.csv':
                    continue
                    
                # Get object details
                file_name = obj['Key']
                file_size = obj['Size']
                upload_date = obj['LastModified'].isoformat()
                file_arn = f"arn:aws:s3:::{bucket}/{file_name}"
                etag = obj['ETag'].strip('"')
                
                # Write row to CSV
                writer.writerow([file_name, file_size, upload_date, file_arn, etag])
        
        # Upload CSV to S3
        s3_client.put_object(
            Bucket=bucket,
            Key='bucket-inventory.csv',
            Body=output.getvalue(),
            ContentType='text/csv'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Inventory CSV created successfully')
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e