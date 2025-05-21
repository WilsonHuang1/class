import boto3
import json
from decimal import Decimal
from boto3.dynamodb.conditions import Key
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
    table = dynamodb.Table('hw09-bids')
    
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
    
    # GET request - retrieve bids for an auction
    if http_method == 'GET':
        # Get auctionId from query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Check for either 'auction' or 'auctionId' parameter
        auction_id = None
        if query_params.get('auction'):
            auction_id = query_params.get('auction')
        elif query_params.get('auctionId'):
            auction_id = query_params.get('auctionId')
        
        if auction_id:
            return get_bids_for_auction(table, auction_id)
        else:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing required parameter: auction or auctionId'})
                })
            }
    
    # Return error for unsupported methods
    return {
        'statusCode': 405,
        'headers': get_cors_headers(),
        'body': json.dumps({
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        })
    }

def get_bids_for_auction(table, auctionId):
    try:
        logger.info(f"Getting bids for auction ID: {auctionId}")
        response = table.query(
            KeyConditionExpression=Key('auctionId').eq(auctionId),
            ScanIndexForward=False  # Sort by sort key (bidAmt) in descending order
        )
        
        bids = response['Items']
        
        # Handle pagination for large datasets
        while 'LastEvaluatedKey' in response:
            response = table.query(
                KeyConditionExpression=Key('auctionId').eq(auctionId),
                ScanIndexForward=False,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            bids.extend(response['Items'])
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 200,
                'body': json.dumps(bids, cls=DecimalEncoder)
            })
        }
    except Exception as e:
        logger.error(f"Error getting bids: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            })
        }