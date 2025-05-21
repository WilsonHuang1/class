"""
S3 Bucket Manager Module

This module provides a command-line interface for managing AWS S3 buckets.
It includes functionality for listing buckets, uploading files, downloading files,
and managing object versions.
"""

import os
import boto3
from botocore.exceptions import ClientError


class S3Manager:
    """Class to manage S3 bucket operations"""

    def __init__(self):
        """Initialize S3 client and bucket state"""
        self.s3 = boto3.client('s3')
        self.current_bucket = None

    def main_menu(self):
        """
        Display and handle the main menu for the S3 bucket manager.
        Provides options for bucket operations and file management.
        """
        while True:
            print("\n=== Main Menu ===")
            print("1. Select S3 Bucket")
            print("2. Backup Local Folder to Bucket")
            print("3. List Bucket Contents")
            print("4. Download File")
            print("5. Generate Presigned URL")
            print("6. List Object Versions")
            print("7. Delete Object")
            print("8. Exit")

            choice = input("Enter choice: ")

            if choice == '1':
                self.list_and_select_bucket()
            elif choice == '2':
                self.backup_local_folder()
            elif choice == '3':
                self.list_bucket_contents()
            elif choice == '4':
                self.download_file()
            elif choice == '5':
                self.generate_presigned_url()
            elif choice == '6':
                self.list_object_versions()
            elif choice == '7':
                self.delete_object()
            elif choice == '8':
                break
            else:
                print("Invalid choice")

    def list_and_select_bucket(self):
        """
        List all available S3 buckets and allow user to select one.
        Sets the current_bucket instance variable.
        """
        response = self.s3.list_buckets()
        buckets = [b['Name'] for b in response['Buckets']]

        if not buckets:
            print("No buckets available!")
            raise IndexError("No buckets available to select")

        print("\nAvailable Buckets:")
        for i, bucket in enumerate(buckets, 1):
            print(f"{i}. {bucket}")

        try:
            choice = int(input("Select bucket (number): ")) - 1
            if choice < 0:
                raise IndexError("Bucket number cannot be negative")
            self.current_bucket = buckets[choice]
            print(f"Selected bucket: {self.current_bucket}")
        except ValueError as exc:
            raise ValueError("Invalid input: Please enter a number") from exc

    def backup_local_folder(self):
        """
        Backup files from a local folder to the selected S3 bucket.
        Maintains folder structure during upload.
        """
        if not self.current_bucket:
            print("No bucket selected!")
            return

        local_path = input("Enter local folder path: ")

        for root, _, files in os.walk(local_path):
            for file in files:
                local_file = os.path.join(root, file)
                s3_path = os.path.relpath(local_file, local_path)
                try:
                    self.s3.upload_file(local_file, self.current_bucket, s3_path)
                    print(f"Uploaded {s3_path}")
                except ClientError as e:
                    print(f"Error uploading {s3_path}: {e}")

    def list_bucket_contents(self):
        """
        List contents of the selected S3 bucket.
        Allows filtering by prefix (folder path).
        """
        if not self.current_bucket:
            print("No bucket selected!")
            return

        prefix = input("Enter folder prefix (optional): ") or ''

        try:
            response = self.s3.list_objects_v2(
                Bucket=self.current_bucket,
                Prefix=prefix
            )
            if 'Contents' not in response:
                print("No objects found")
                return

            for obj in response['Contents']:
                print(f"{obj['Key']} ({obj['Size']} bytes)")
        except ClientError as e:
            print(f"Error listing contents: {e}")

    def download_file(self):
        """
        Download a file from the selected S3 bucket to a local path.
        """
        if not self.current_bucket:
            print("No bucket selected!")
            return

        object_key = input("Enter object key to download: ")
        local_path = input("Enter local save path: ")

        try:
            self.s3.download_file(self.current_bucket, object_key, local_path)
            print(f"Downloaded {object_key} to {local_path}")
        except ClientError as e:
            print(f"Error downloading file: {e}")

    def generate_presigned_url(self):
        """
        Generate a presigned URL for an object in the selected bucket.
        URL is valid for 1 hour by default.
        """
        if not self.current_bucket:
            print("No bucket selected!")
            return

        object_key = input("Enter object key: ")
        if not object_key:
            print("Object key cannot be empty!")
            return

        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.current_bucket, 'Key': object_key},
                ExpiresIn=3600
            )
            print(f"Presigned URL (valid 1 hour): {url}")
        except ClientError as e:
            print(f"Error generating URL: {e}")

    def list_object_versions(self):
        """
        List all versions of an object in the selected bucket.
        """
        if not self.current_bucket:
            print("No bucket selected!")
            return

        object_key = input("Enter object key: ")
        try:
            response = self.s3.list_object_versions(
                Bucket=self.current_bucket,
                Prefix=object_key
            )
            for version in response.get('Versions', []):
                print(f"Version ID: {version['VersionId']}")
                print(f"Last Modified: {version['LastModified']}")
                print(f"Size: {version['Size']} bytes\n")
        except ClientError as e:
            print(f"Error listing versions: {e}")

    def delete_object(self):
        """
        Delete an object from the selected bucket.
        """
        if not self.current_bucket:
            print("No bucket selected!")
            return

        object_key = input("Enter object key to delete: ")
        try:
            self.s3.delete_object(Bucket=self.current_bucket, Key=object_key)
            print(f"Deleted {object_key}")
        except ClientError as e:
            print(f"Error deleting object: {e}")


def main():
    """Main entry point for the application"""
    manager = S3Manager()
    manager.main_menu()


if __name__ == "__main__":
    main()
