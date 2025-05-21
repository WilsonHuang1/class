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
    table = dynamodb.Table('hw09-auctions')
    
    # Log event for debugging
    logger.info("Event received: %s", json.dumps(event))
    
    # Handle OPTIONS method for CORS preflight
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 200,
                'body': json.dumps({'message': 'CORS preflight successful'})
            })
        }
    
    http_method = event['httpMethod']
    
    # GET request - retrieve auction(s)
    if http_method == 'GET':
        # Check if auctionId is provided in path parameters
        path_parameters = event.get('pathParameters', {}) or {}
        if path_parameters and path_parameters.get('auctionId'):
            return get_single_auction(table, path_parameters['auctionId'])
        else:
            return get_all_auctions(table)
    
    # POST request - create a new auction
    elif http_method == 'POST':
        return create_auction(table, event)
    
    # Return error for unsupported methods
    return {
        'statusCode': 405,
        'headers': get_cors_headers(),
        'body': json.dumps({
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        })
    }

def get_single_auction(table, auctionId):
    try:
        logger.info(f"Getting auction with ID: {auctionId}")
        response = table.get_item(Key={'auctionId': auctionId})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'statusCode': 404,
                    'body': json.dumps({'error': f"Auction with ID '{auctionId}' not found"})
                })
            }
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 200,
                'body': json.dumps(response['Item'], cls=DecimalEncoder)
            })
        }
    except Exception as e:
        logger.error(f"Error getting auction: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            })
        }

def get_all_auctions(table):
    try:
        logger.info("Getting all auctions")
        response = table.scan()
        auctions = response['Items']
        
        # Handle pagination for large datasets
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            auctions.extend(response['Items'])
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 200,
                'body': json.dumps(auctions, cls=DecimalEncoder)
            })
        }
    except Exception as e:
        logger.error(f"Error getting all auctions: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            })
        }

def create_auction(table, event):
    try:
        # Parse the request body
        body = json.loads(event['body'])
        logger.info(f"Creating auction: {json.dumps(body)}")
        
        # Validate required fields
        required_fields = ['auctionId', 'itemName', 'reserve', 'description', 'status']
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps({
                        'statusCode': 400,
                        'body': json.dumps({'error': f"Missing required field: {field}"})
                    })
                }
        
        # Check if auction already exists
        existing_auction = table.get_item(Key={'auctionId': body['auctionId']})
        if 'Item' in existing_auction:
            return {
                'statusCode': 409,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'statusCode': 409,
                    'body': json.dumps({'error': f"Auction with ID '{body['auctionId']}' already exists"})
                })
            }
        
        # Convert reserve to Decimal for DynamoDB
        if 'reserve' in body:
            body['reserve'] = Decimal(str(body['reserve']))
        
        # Ensure winningUserId is included (can be empty)
        if 'winningUserId' not in body:
            body['winningUserId'] = ""
        
        # Insert the new auction
        table.put_item(Item=body)
        
        return {
            'statusCode': 201,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 201,
                'body': json.dumps({'message': 'Auction created successfully'})
            })
        }
    except Exception as e:
        logger.error(f"Error creating auction: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            })
        }