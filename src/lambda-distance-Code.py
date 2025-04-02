import json
import boto3
from botocore.exceptions import ClientError
import os
import decimal

# Initialize DynamoDB and S3 clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# DynamoDB table name and S3 bucket name for distance data
TABLE_NAME = os.environ.get('TABLE_NAME', 'SensorData')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'distances3')

# Helper function to convert Decimal to float for JSON serialization
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    print("Querying DynamoDB for distance data...")
    try:
        # Query data from DynamoDB
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('SensorID').eq('distance')
        )
        items = response.get('Items', [])
        if not items:
            print("No items found for the specified SensorID: distance.")
            return {
                'statusCode': 200,
                'body': json.dumps('No data found for SensorID: distance')
            }
        print(f"Queried Items: {json.dumps(items, default=decimal_default)}")
    except ClientError as e:
        error_message = e.response['Error']['Message']
        print(f"Error querying table: {error_message}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Failed to query DynamoDB table: {error_message}')
        }

    print("Transforming data...")
    formatted_items = []
    for item in items:
        payload = item.get('payload')
        if isinstance(payload, dict):  # Ensure payload is a dictionary
            formatted_item = {
                "SensorID": payload.get("SensorID", "unknown"),
                "TS": int(payload.get("TS", 0)),  # Convert to int
                "Reading": float(payload.get("Reading", 0.0)),  # Convert to float
                "Units": payload.get("Units", "unknown")
            }
            formatted_items.append(formatted_item)

    if not formatted_items:
        print("No valid items found in payloads.")
        return {
            'statusCode': 200,
            'body': json.dumps('No valid items to transfer')
        }

    print(f"Formatted Items: {json.dumps(formatted_items, default=decimal_default)}")

    print("Writing distance data to S3...")
    try:
        json_data = json.dumps(formatted_items, default=decimal_default)
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key='distance_data.json',
            Body=json_data,
            ContentType='application/json',
            ServerSideEncryption='AES256'
        )
        print("Distance data successfully written to S3")
    except ClientError as e:
        error_message = e.response['Error']['Message']
        print(f"Error uploading distance data to S3: {error_message}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Failed to upload distance data to S3: {error_message}')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully transferred distance data to S3')
    }
