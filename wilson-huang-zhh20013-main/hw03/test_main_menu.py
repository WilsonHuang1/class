"""
Test module for S3Manager with comprehensive edge cases.

This module contains extensive test cases for the S3Manager class,
testing various S3 bucket operations including edge cases and error conditions.
"""

import os
import tempfile
import unittest
from unittest.mock import patch
import json

import boto3
from moto import mock_aws
from botocore.exceptions import ClientError

from main_menu import S3Manager


@mock_aws
class BaseS3Test(unittest.TestCase):
    """Base test class for S3 operations."""

    def setUp(self):
        """Set up test environment before each test."""
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

        self.s3 = boto3.client('s3', region_name='us-east-1')
        self.test_bucket = "test-bucket"
        self.empty_bucket = "empty-bucket"
        self.special_bucket = "test-bucket-with-special-chars"

        self.s3.create_bucket(Bucket=self.test_bucket)
        self.s3.create_bucket(Bucket=self.empty_bucket)
        self.s3.create_bucket(Bucket=self.special_bucket)

        self.s3.put_bucket_versioning(
            Bucket=self.test_bucket,
            VersioningConfiguration={'Status': 'Enabled'}
        )

        self.test_files = {
            'test1.txt': b'Test content 1',
            'test2.txt': b'Test content 2',
            'folder/test3.txt': b'Test content 3',
            'test space.txt': b'Test content with space',
            'test#special.txt': b'Test content with special chars',
            'empty.txt': b'',
            'folder/subfolder/nested.txt': b'Nested content',
            'large.txt': b'x' * 1024 * 1024,
            'test.json': json.dumps({'key': 'value'}).encode(),
            'unicode_名前.txt': b'Unicode filename test'
        }

        for key, content in self.test_files.items():
            self.s3.put_object(Bucket=self.test_bucket, Key=key, Body=content)

        self.manager = S3Manager()
        self.manager.s3 = self.s3

    def tearDown(self):
        """Clean up after each test."""
        self.manager.current_bucket = None


@mock_aws
class TestBucketOperations(BaseS3Test):
    """Test cases for bucket operations."""

    def test_list_and_select_bucket_normal(self):
        """Test normal bucket selection."""
        with patch('builtins.input', return_value='1'):
            self.manager.list_and_select_bucket()
            self.assertEqual(self.manager.current_bucket, self.test_bucket)

    def test_list_and_select_bucket_empty_list(self):
        """Test bucket selection with no buckets."""
        for bucket in self.s3.list_buckets()['Buckets']:
            version_response = self.s3.list_object_versions(
                Bucket=bucket['Name']
            )
            objects_to_delete = []
            for version in version_response.get('Versions', []):
                objects_to_delete.append({
                    'Key': version['Key'],
                    'VersionId': version['VersionId']
                })
            if objects_to_delete:
                self.s3.delete_objects(
                    Bucket=bucket['Name'],
                    Delete={'Objects': objects_to_delete}
                )
            self.s3.delete_bucket(Bucket=bucket['Name'])
        with self.assertRaises(IndexError):
            self.manager.list_and_select_bucket()

    def test_list_and_select_bucket_invalid_index(self):
        """Test selecting bucket with invalid index."""
        with patch('builtins.input', return_value='999'):
            with self.assertRaises(IndexError):
                self.manager.list_and_select_bucket()

    def test_list_and_select_bucket_non_numeric(self):
        """Test selecting bucket with non-numeric input."""
        with patch('builtins.input', return_value='abc'):
            with self.assertRaises(ValueError):
                self.manager.list_and_select_bucket()

    def test_list_and_select_bucket_negative_index(self):
        """Test selecting bucket with negative index."""
        with patch('builtins.input', return_value='-1'):
            with self.assertRaises(IndexError):
                self.manager.list_and_select_bucket()


@mock_aws
class TestFileOperations(BaseS3Test):
    """Test cases for file operations."""

    def test_backup_local_folder_empty(self):
        """Test backing up an empty folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.current_bucket = self.test_bucket
            with patch('builtins.input', return_value=temp_dir):
                self.manager.backup_local_folder()
            response = self.s3.list_objects_v2(Bucket=self.test_bucket)
            initial_count = len(self.test_files)
            self.assertEqual(len(response.get('Contents', [])), initial_count)

    def test_backup_local_folder_nested_structure(self):
        """Test backing up nested folder structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            folder_path = os.path.join(temp_dir, 'folder1', 'folder2')
            os.makedirs(folder_path)
            file_path = os.path.join(folder_path, 'test.txt')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('test')

            self.manager.current_bucket = self.test_bucket
            with patch('builtins.input', return_value=temp_dir):
                self.manager.backup_local_folder()

            response = self.s3.get_object(
                Bucket=self.test_bucket,
                Key='folder1/folder2/test.txt'
            )
            self.assertEqual(response['Body'].read().decode(), 'test')

    def test_backup_local_folder_special_characters(self):
        """Test backing up files with special characters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            special_files = {
                'test space.txt': 'content with spaces',
                'test#hash.txt': 'content with hash',
                'test$dollar.txt': 'content with dollar',
                'test@at.txt': 'content with at',
                'test你好.txt': 'content with unicode'
            }
            for filename, content in special_files.items():
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            self.manager.current_bucket = self.test_bucket
            with patch('builtins.input', return_value=temp_dir):
                self.manager.backup_local_folder()

            for filename, content in special_files.items():
                response = self.s3.get_object(
                    Bucket=self.test_bucket,
                    Key=filename
                )
                self.assertEqual(response['Body'].read().decode(), content)

    def test_download_file_normal(self):
        """Test downloading a normal file."""
        self.manager.current_bucket = self.test_bucket
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            with patch('builtins.input',
                      side_effect=['test1.txt', temp_file.name]):
                self.manager.download_file()
                with open(temp_file.name, 'rb') as f:
                    content = f.read()
                    self.assertEqual(content, self.test_files['test1.txt'])

    def test_download_file_nonexistent(self):
        """Test downloading non-existent file."""
        self.manager.current_bucket = self.test_bucket
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            with patch('builtins.input',
                      side_effect=['nonexistent.txt', temp_file.name]):
                self.manager.download_file()

    def test_download_file_special_chars(self):
        """Test downloading file with special characters."""
        self.manager.current_bucket = self.test_bucket
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            with patch('builtins.input',
                      side_effect=['test space.txt', temp_file.name]):
                self.manager.download_file()
                with open(temp_file.name, 'rb') as f:
                    content = f.read()
                    self.assertEqual(
                        content,
                        self.test_files['test space.txt']
                    )


@mock_aws
class TestVersionOperations(BaseS3Test):
    """Test cases for version operations."""

    def test_list_object_versions_normal(self):
        """Test listing versions for normal file."""
        key = 'versioned.txt'
        self.manager.current_bucket = self.test_bucket

        for i in range(3):
            self.s3.put_object(
                Bucket=self.test_bucket,
                Key=key,
                Body=f'Version {i}'.encode()
            )

        with patch('builtins.input', return_value=key):
            self.manager.list_object_versions()

    def test_list_object_versions_deleted_object(self):
        """Test listing versions for a deleted object."""
        key = 'deleted_file.txt'
        self.manager.current_bucket = self.test_bucket

        self.s3.put_object(
            Bucket=self.test_bucket,
            Key=key,
            Body=b'Original content'
        )
        self.s3.delete_object(
            Bucket=self.test_bucket,
            Key=key
        )

        with patch('builtins.input', return_value=key):
            self.manager.list_object_versions()

    def test_list_object_versions_multiple_changes(self):
        """Test listing versions with multiple changes."""
        key = 'multiple_versions.txt'
        self.manager.current_bucket = self.test_bucket

        self.s3.put_object(Bucket=self.test_bucket, Key=key, Body=b'Version 1')
        self.s3.put_object(Bucket=self.test_bucket, Key=key, Body=b'Version 2')
        self.s3.delete_object(Bucket=self.test_bucket, Key=key)
        self.s3.put_object(Bucket=self.test_bucket, Key=key, Body=b'Version 3')

        with patch('builtins.input', return_value=key):
            self.manager.list_object_versions()


@mock_aws
class TestURLOperations(BaseS3Test):
    """Test cases for URL operations."""

    def test_generate_presigned_url_normal(self):
        """Test generating presigned URL for normal file."""
        self.manager.current_bucket = self.test_bucket
        with patch('builtins.input', return_value='test1.txt'):
            self.manager.generate_presigned_url()

    def test_generate_presigned_url_special_chars(self):
        """Test generating presigned URL with special characters."""
        self.manager.current_bucket = self.test_bucket
        with patch('builtins.input', return_value='test space.txt'):
            self.manager.generate_presigned_url()

    def test_generate_presigned_url_nonexistent(self):
        """Test generating presigned URL for nonexistent file."""
        self.manager.current_bucket = self.test_bucket
        with patch('builtins.input', return_value='nonexistent.txt'):
            self.manager.generate_presigned_url()


@mock_aws
class TestDeleteOperations(BaseS3Test):
    """Test cases for delete operations."""

    def test_delete_object_normal(self):
        """Test deleting a normal file."""
        key = 'test1.txt'
        self.manager.current_bucket = self.test_bucket
        with patch('builtins.input', return_value=key):
            self.manager.delete_object()
            with self.assertRaises(ClientError):
                self.s3.head_object(Bucket=self.test_bucket, Key=key)

    def test_delete_object_special_chars(self):
        """Test deleting file with special characters."""
        key = 'test space.txt'
        self.manager.current_bucket = self.test_bucket
        with patch('builtins.input', return_value=key):
            self.manager.delete_object()
            with self.assertRaises(ClientError):
                self.s3.head_object(Bucket=self.test_bucket, Key=key)

    def test_delete_object_nonexistent(self):
        """Test deleting nonexistent file."""
        self.manager.current_bucket = self.test_bucket
        with patch('builtins.input', return_value='nonexistent.txt'):
            self.manager.delete_object()


@mock_aws
class TestNoBucketOperations(BaseS3Test):
    """Test cases for operations with no bucket selected."""

    def test_no_bucket_selected_all_operations(self):
        """Test all operations with no bucket selected."""
        self.manager.current_bucket = None
        operations = [
            self.manager.backup_local_folder,
            self.manager.list_bucket_contents,
            self.manager.download_file,
            self.manager.generate_presigned_url,
            self.manager.list_object_versions,
            self.manager.delete_object
        ]

        for operation in operations:
            operation()

    def test_no_bucket_selected_with_input(self):
        """Test operations with no bucket but with user input."""
        self.manager.current_bucket = None
        with patch('builtins.input', return_value='test.txt'):
            self.manager.download_file()
            self.manager.generate_presigned_url()
            self.manager.list_object_versions()
            self.manager.delete_object()


if __name__ == '__main__':
    unittest.main()
