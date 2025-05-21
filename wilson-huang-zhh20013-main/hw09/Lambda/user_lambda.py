import boto3
import json
from decimal import Decimal
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Custom JSON encoder to handle Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) if obj % 1 != 0 else int(obj)
        return super(DecimalEncoder, self).default(obj)

# Common headers for all responses
def get_cors_headers():
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
    }

def lambda_handler(event, context):
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('hw09-user')
    
    # Log event for debugging
    logger.info("Event received: %s", json.dumps(event))
    
    # Handle OPTIONS method for CORS preflight
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({'message': 'CORS preflight successful'})
        }
    
    # GET request - retrieve user(s)
    if event['httpMethod'] == 'GET':
        # Check if userId is provided in path parameters
        path_parameters = event.get('pathParameters', {}) or {}
        if path_parameters and path_parameters.get('userId'):
            return get_single_user(table, path_parameters['userId'])
        else:
            return get_all_users(table)
    
    # POST request - create a new user
    elif event['httpMethod'] == 'POST':
        return create_user(table, event)
    
    # Return error for unsupported methods
    return {
        'statusCode': 405,
        'headers': get_cors_headers(),
        'body': json.dumps({'error': 'Method not allowed'})
    }

def get_single_user(table, userId):
    try:
        logger.info(f"Getting user with ID: {userId}")
        response = table.get_item(Key={'userId': userId})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': f"User with ID '{userId}' not found"})
            }
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(response['Item'], cls=DecimalEncoder)
        }
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_all_users(table):
    try:
        logger.info("Getting all users")
        response = table.scan()
        users = response['Items']
        
        # Handle pagination for large datasets
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            users.extend(response['Items'])
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 200,
                'body': json.dumps(users, cls=DecimalEncoder)
            })
        }
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            })
        }

def create_user(table, event):
    try:
        # Parse the request body
        body = json.loads(event['body'])
        logger.info(f"Creating user: {json.dumps(body)}")
        
        # Validate required fields
        required_fields = ['userId', 'name', 'acctBalance']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps({'error': f"Missing required field: {field}"})
                }
        
        # Check if user already exists
        existing_user = table.get_item(Key={'userId': body['userId']})
        if 'Item' in existing_user:
            return {
                'statusCode': 409,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': f"User with ID '{body['userId']}' already exists"})
            }
        
        # Convert acctBalance to Decimal for DynamoDB
        if 'acctBalance' in body:
            body['acctBalance'] = Decimal(str(body['acctBalance']))
        
        # Insert the new user
        table.put_item(Item=body)
        
        return {
            'statusCode': 201,
            'headers': get_cors_headers(),
            'body': json.dumps({'message': 'User created successfully'})
        }
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': str(e)})
        }