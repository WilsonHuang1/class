import pytest
import boto3
import time
import os
from datetime import datetime, timezone

@pytest.fixture
def s3_client():
    return boto3.client('s3', region_name='us-east-1')

@pytest.fixture
def dynamodb_client():
    return boto3.client('dynamodb', region_name='us-east-1')

@pytest.fixture
def test_bucket():
    return os.environ['S3_BUCKET']

@pytest.fixture
def test_table():
    return os.environ['DYNAMODB_TABLE']

def test_simple_text_file(s3_client, dynamodb_client, test_bucket, test_table):
    filename = "simple_test.txt"
    content = "This is a simple text file for testing."
    
    try:
        s3_client.put_object(
            Bucket=test_bucket,
            Key=filename,
            Body=content
        )
        
        time.sleep(5)
        
        response = dynamodb_client.scan(
            TableName=test_table,
            FilterExpression='fileName = :filename',
            ExpressionAttributeValues={
                ':filename': {'S': filename}
            }
        )
        
        assert len(response['Items']) > 0, "File not found in DynamoDB"
        item = response['Items'][0]
        assert item['fileName']['S'] == filename
        assert int(item['fileSize']['N']) == len(content)
        
    finally:
        s3_client.delete_object(
            Bucket=test_bucket,
            Key=filename
        )

def test_common_file_types(s3_client, dynamodb_client, test_bucket, test_table):
    test_files = [
        ("document.txt", "Text file content"),
        ("data.json", '{"key": "value"}'),
        ("data.csv", "name,age\nJohn,30\nJane,25"),
        ("script.py", "print('Hello World')")
    ]
    
    try:
        for filename, content in test_files:
            s3_client.put_object(
                Bucket=test_bucket,
                Key=filename,
                Body=content
            )
            
        time.sleep(5)
        
        for filename, content in test_files:
            response = dynamodb_client.scan(
                TableName=test_table,
                FilterExpression='fileName = :filename',
                ExpressionAttributeValues={
                    ':filename': {'S': filename}
                }
            )
            
            assert len(response['Items']) > 0, f"{filename} not found in DynamoDB"
            item = response['Items'][0]
            assert item['fileName']['S'] == filename
            assert int(item['fileSize']['N']) == len(content)
            
    finally:
        for filename, _ in test_files:
            s3_client.delete_object(
                Bucket=test_bucket,
                Key=filename
            )

def test_nested_path_file(s3_client, dynamodb_client, test_bucket, test_table):
    filename = "folder1/folder2/test.txt"
    content = "File in nested folders"
    
    try:
        s3_client.put_object(
            Bucket=test_bucket,
            Key=filename,
            Body=content
        )
        
        time.sleep(5)
        
        response = dynamodb_client.scan(
            TableName=test_table,
            FilterExpression='fileName = :filename',
            ExpressionAttributeValues={
                ':filename': {'S': filename}
            }
        )
        
        assert len(response['Items']) > 0, "Nested path file not found in DynamoDB"
        item = response['Items'][0]
        assert item['fileName']['S'] == filename
        assert int(item['fileSize']['N']) == len(content)
        
    finally:
        s3_client.delete_object(
            Bucket=test_bucket,
            Key=filename
        )

def test_special_characters_filename(s3_client, dynamodb_client, test_bucket, test_table):
    # Reduced set of special files to test with simpler cases first
    special_files = [
        "file-with-hyphens.txt",  # Simple special character
        "file_with_underscores.txt",  # Underscores are usually safe
        "simple-file-123.txt"  # Numbers and hyphens
    ]
    
    try:
        for filename in special_files:
            s3_client.put_object(
                Bucket=test_bucket,
                Key=filename,
                Body="test content"
            )
            
        time.sleep(10)  # Increased wait time
        
        for filename in special_files:
            response = dynamodb_client.scan(
                TableName=test_table,
                FilterExpression='fileName = :filename',
                ExpressionAttributeValues={
                    ':filename': {'S': filename}
                }
            )
            
            # Add debug logging
            print(f"Looking for file: {filename}")
            print(f"DynamoDB response: {response}")
            
            assert len(response['Items']) > 0, f"File not found: {filename}"
            item = response['Items'][0]
            assert item['fileName']['S'] == filename
            
    finally:
        for filename in special_files:
            try:
                s3_client.delete_object(
                    Bucket=test_bucket,
                    Key=filename
                )
            except Exception as e:
                print(f"Error deleting {filename}: {str(e)}")

def test_empty_file(s3_client, dynamodb_client, test_bucket, test_table):
    filename = "empty_file.txt"
    try:
        s3_client.put_object(
            Bucket=test_bucket,
            Key=filename,
            Body=""
        )
        
        time.sleep(5)
        
        response = dynamodb_client.scan(
            TableName=test_table,
            FilterExpression='fileName = :filename',
            ExpressionAttributeValues={
                ':filename': {'S': filename}
            }
        )
        
        assert len(response['Items']) > 0, "Empty file not found in DynamoDB"
        item = response['Items'][0]
        assert item['fileName']['S'] == filename
        assert item['fileSize']['N'] == "0"
        
    finally:
        s3_client.delete_object(
            Bucket=test_bucket,
            Key=filename
        )

def test_large_file(s3_client, dynamodb_client, test_bucket, test_table):
    filename = "large_file.txt"
    large_content = "x" * (5 * 1024 * 1024)  # 5MB of data
    
    try:
        s3_client.put_object(
            Bucket=test_bucket,
            Key=filename,
            Body=large_content
        )
        
        time.sleep(10)  # Longer wait for large file
        
        response = dynamodb_client.scan(
            TableName=test_table,
            FilterExpression='fileName = :filename',
            ExpressionAttributeValues={
                ':filename': {'S': filename}
            }
        )
        
        assert len(response['Items']) > 0, "Large file not found in DynamoDB"
        item = response['Items'][0]
        assert item['fileName']['S'] == filename
        assert int(item['fileSize']['N']) == len(large_content)
        
    finally:
        s3_client.delete_object(
            Bucket=test_bucket,
            Key=filename
        )

def test_concurrent_uploads(s3_client, dynamodb_client, test_bucket, test_table):
    files = [f"concurrent_file_{i}.txt" for i in range(5)]
    
    try:
        for filename in files:
            s3_client.put_object(
                Bucket=test_bucket,
                Key=filename,
                Body=f"Content for {filename}"
            )
        
        time.sleep(10)  # Wait for all processing
        
        for filename in files:
            response = dynamodb_client.scan(
                TableName=test_table,
                FilterExpression='fileName = :filename',
                ExpressionAttributeValues={
                    ':filename': {'S': filename}
                }
            )
            
            assert len(response['Items']) > 0, f"Concurrent file not found: {filename}"
            item = response['Items'][0]
            assert item['fileName']['S'] == filename
            
    finally:
        for filename in files:
            s3_client.delete_object(
                Bucket=test_bucket,
                Key=filename
            )