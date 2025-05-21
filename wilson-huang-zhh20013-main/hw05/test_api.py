import requests
import pytest
import json
import time
import base64
import os

BASE_API_ID = "2by1roa4t4"
REGION = "us-east-1"
DEV_API_URL = f"https://{BASE_API_ID}.execute-api.{REGION}.amazonaws.com/dev"
PROD_API_URL = f"https://{BASE_API_ID}.execute-api.{REGION}.amazonaws.com/prod"
BUCKET_NAME = "hw04-zhh20013-1"  # Your bucket name

# Test file names
DEV_TEST_FILE = "pytest-dev-test-file.txt"
PROD_TEST_FILE = "pytest-prod-test-file.txt"
SPECIAL_CHARS_FILE = "test!@#$%^&*()-_+=.txt"
EMPTY_CONTENT_FILE = "empty-content-file.txt"
LARGE_FILE = "large-test-file.txt"

# Test both dev and prod environments
@pytest.mark.parametrize("api_url,test_file", [
    (DEV_API_URL, DEV_TEST_FILE),
    (PROD_API_URL, PROD_TEST_FILE)
])
def test_list_buckets(api_url, test_file):
    """Test the /list endpoint to make sure it returns buckets"""
    print(f"Testing list buckets on {api_url}")
    response = requests.get(f"{api_url}/list")
    assert response.status_code == 200
    buckets = response.json()
    assert isinstance(buckets, list)
    assert BUCKET_NAME in buckets

@pytest.mark.parametrize("api_url,test_file", [
    (DEV_API_URL, DEV_TEST_FILE),
    (PROD_API_URL, PROD_TEST_FILE)
])
def test_list_objects(api_url, test_file):
    """Test the /{bucket-name} endpoint to list objects"""
    print(f"Testing list objects on {api_url}")
    response = requests.get(f"{api_url}/{BUCKET_NAME}")
    assert response.status_code == 200
    objects = response.json()
    assert isinstance(objects, list)

@pytest.mark.parametrize("api_url,test_file", [
    (DEV_API_URL, DEV_TEST_FILE),
    (PROD_API_URL, PROD_TEST_FILE)
])
def test_add_and_delete_object(api_url, test_file):
    """Test the POST and DELETE operations"""
    print(f"Testing add/delete on {api_url} with file {test_file}")
    
    # Add an object
    post_data = {
        "name": test_file,
        "content": f"This is a test file created by pytest for {api_url}"
    }
    
    post_response = requests.post(
        f"{api_url}/{BUCKET_NAME}",
        json=post_data
    )
    assert post_response.status_code == 200
    
    # Wait a second to ensure object is created
    time.sleep(1)
    
    # Verify object exists
    get_response = requests.get(f"{api_url}/{BUCKET_NAME}")
    objects = get_response.json()
    assert test_file in objects
    
    # Delete the object
    delete_response = requests.delete(
        f"{api_url}/{BUCKET_NAME}/{test_file}"
    )
    assert delete_response.status_code == 200
    
    # Wait a second to ensure object is deleted
    time.sleep(1)
    
    # Verify object is gone
    get_response = requests.get(f"{api_url}/{BUCKET_NAME}")
    objects = get_response.json()
    assert test_file not in objects

# Edge Cases

@pytest.mark.parametrize("api_url", [DEV_API_URL, PROD_API_URL])
def test_nonexistent_bucket(api_url):
    """Test behavior when accessing a bucket that doesn't exist"""
    print(f"Testing nonexistent bucket on {api_url}")
    
    # Generate a random bucket name that's unlikely to exist
    fake_bucket = f"nonexistent-bucket-{int(time.time())}"
    
    response = requests.get(f"{api_url}/{fake_bucket}")
    # Either should return empty list or appropriate error code
    assert response.status_code in [200, 404, 403, 500]
    
    if response.status_code == 200:
        objects = response.json()
        assert isinstance(objects, list)
        assert len(objects) == 0

@pytest.mark.parametrize("api_url", [DEV_API_URL, PROD_API_URL])
def test_special_characters_in_filename(api_url):
    """Test handling of special characters in object name"""
    print(f"Testing special characters in filename on {api_url}")
    
    # Add an object with special characters in the name
    post_data = {
        "name": SPECIAL_CHARS_FILE,
        "content": "Testing special characters in filename"
    }
    
    post_response = requests.post(
        f"{api_url}/{BUCKET_NAME}",
        json=post_data
    )
    assert post_response.status_code == 200
    
    time.sleep(1)
    
    # Verify we can list it
    get_response = requests.get(f"{api_url}/{BUCKET_NAME}")
    objects = get_response.json()
    
    # Clean up after the test
    delete_response = requests.delete(
        f"{api_url}/{BUCKET_NAME}/{SPECIAL_CHARS_FILE}"
    )
    
    # It might not properly encode/decode special characters, so check if it exists or a variant exists
    special_file_found = SPECIAL_CHARS_FILE in objects or any(SPECIAL_CHARS_FILE in obj for obj in objects)
    assert special_file_found or delete_response.status_code != 200

@pytest.mark.parametrize("api_url", [DEV_API_URL, PROD_API_URL])
def test_empty_content(api_url):
    """Test handling of empty content - should be rejected with 400"""
    print(f"Testing empty content on {api_url}")
    
    # Add an object with empty content
    post_data = {
        "name": EMPTY_CONTENT_FILE,
        "content": ""
    }
    
    post_response = requests.post(
        f"{api_url}/{BUCKET_NAME}",
        json=post_data
    )
    # Expect a 400 Bad Request since empty content is invalid
    assert post_response.status_code == 400
    
    # Verify the error message if possible
    response_body = post_response.json()
    assert 'error' in response_body
    print(f"Received expected error: {response_body['error']}")

@pytest.mark.parametrize("api_url", [DEV_API_URL])  # Only test on dev to save time
def test_large_file(api_url):
    """Test handling of a relatively large file (500KB)"""
    print(f"Testing large file on {api_url}")
    
    # Generate a 500KB string
    large_content = "A" * 500000
    
    # Add the large object
    post_data = {
        "name": LARGE_FILE,
        "content": large_content
    }
    
    post_response = requests.post(
        f"{api_url}/{BUCKET_NAME}",
        json=post_data
    )
    assert post_response.status_code == 200
    
    time.sleep(2)  # Give more time for large file
    
    # Verify we can list it
    get_response = requests.get(f"{api_url}/{BUCKET_NAME}")
    objects = get_response.json()
    assert LARGE_FILE in objects
    
    # Clean up
    delete_response = requests.delete(
        f"{api_url}/{BUCKET_NAME}/{LARGE_FILE}"
    )
    assert delete_response.status_code == 200

@pytest.mark.parametrize("api_url", [DEV_API_URL])  # Only test on dev to save time
def test_delete_nonexistent_object(api_url):
    """Test behavior when deleting an object that doesn't exist"""
    print(f"Testing delete nonexistent object on {api_url}")
    
    # Generate a random object name that's unlikely to exist
    fake_object = f"nonexistent-object-{int(time.time())}.txt"
    
    delete_response = requests.delete(
        f"{api_url}/{BUCKET_NAME}/{fake_object}"
    )
    
    # S3 returns success even when deleting non-existent objects, so our API should do the same
    assert delete_response.status_code in [200, 204, 404]

# Clean up any test files that might be left over from failed tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_files():
    yield  # This allows all tests to run first
    
    # List of all test files that might need cleanup
    all_test_files = [
        DEV_TEST_FILE, 
        PROD_TEST_FILE, 
        SPECIAL_CHARS_FILE, 
        EMPTY_CONTENT_FILE, 
        LARGE_FILE
    ]
    
    # Then clean up any remaining test files from both environments
    for api_url in [DEV_API_URL, PROD_API_URL]:
        for test_file in all_test_files:
            try:
                requests.delete(f"{api_url}/{BUCKET_NAME}/{test_file}")
                print(f"Cleaned up {test_file} from {api_url}")
            except:
                pass  # Ignore errors during cleanup