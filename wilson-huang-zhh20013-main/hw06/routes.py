from flask import request, render_template, jsonify
from resource_s3 import S3Resource
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the S3 bucket name from environment variable or use a default for local testing
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'your-default-bucket-name')
s3_resource = S3Resource(BUCKET_NAME)

def configure_routes(app):
    '''Setup all the API routes'''

    @app.route('/')
    def homepage():
        '''Show the main screen. This is the main entry point for the webapp'''
        logger.info("Rendering index page")
        return render_template("index.html")

    @app.route('/list_objects')
    def list_files():
        '''Return the list of objects in the bucket as JSON'''
        logger.info("API call: list_objects")
        objects = s3_resource.list_objects()
        # Make sure objects is a list or dictionary, not a Response
        return jsonify(objects)
    
    @app.route('/list_buckets')
    def list_buckets():
        '''Return the list of all buckets as JSON'''
        logger.info("API call: list_buckets")
        buckets = s3_resource.list_buckets()
        return jsonify(buckets)

    @app.route('/set_bucket', methods=['POST'])
    def set_bucket():
        '''Change the current bucket'''
        logger.info("API call: set_bucket")
        bucket_name = request.json.get('bucket')
        if not bucket_name:
            logger.warning("No bucket name provided")
            return jsonify({'error': 'No bucket name provided'}), 400
            
        success = s3_resource.set_bucket(bucket_name)
        if success:
            logger.info(f"Successfully changed to bucket {bucket_name}")
            return jsonify({'message': 'Bucket changed successfully'})
        else:
            logger.error(f"Failed to change to bucket {bucket_name}")
            return jsonify({'error': 'Failed to change bucket'}), 500

    @app.route('/upload', methods=['POST'])
    def upload_file():
        '''Process file upload and return status as JSON'''
        logger.info("API call: upload file")
        if request.method == 'POST':
            if 'file' not in request.files:
                logger.warning("No file part in the request")
                return jsonify({'error': 'No file part'}), 400
            
            file = request.files['file']
            if file.filename == '':
                logger.warning("No file selected")
                return jsonify({'error': 'No selected file'}), 400
            
            # Make sure method name matches what's in resource_s3.py
            success = s3_resource.upload_file_to_s3(file, file.filename)
            if success:
                logger.info(f"Successfully uploaded {file.filename}")
                return jsonify({'message': 'File uploaded successfully'})
            else:
                logger.error("Upload failed")
                return jsonify({'error': 'Upload failed'}), 500
                
        return jsonify({'error': 'Method not allowed'}), 405

    @app.route('/get_thumbnail')
    def get_thumbnail():
        '''Get a presigned URL for an object'''
        logger.info("API call: get_thumbnail")
        object_key = request.args.get('obj')
        if not object_key:
            logger.warning("No object key provided")
            return jsonify({'error': 'No object key provided'}), 400
            
        url = s3_resource.generate_presigned_url(object_key)
        if url:
            logger.info(f"Generated presigned URL for {object_key}")
            return jsonify({'url': url})
        else:
            logger.error(f"Failed to generate URL for {object_key}")
            return jsonify({'error': 'Failed to generate URL'}), 500
        
    @app.route('/delete_object', methods=['POST'])
    def delete_object():
        '''Delete an object from the bucket'''
        logger.info("API call: delete_object")
        object_key = request.json.get('key')
        if not object_key:
            logger.warning("No object key provided")
            return jsonify({'error': 'No object key provided'}), 400
            
        success = s3_resource.delete_object(object_key)
        if success:
            logger.info(f"Successfully deleted {object_key}")
            return jsonify({'message': 'Object deleted successfully'})
        else:
            logger.error(f"Failed to delete {object_key}")
            return jsonify({'error': 'Failed to delete object'}), 500
        