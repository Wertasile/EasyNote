import simplejson as json
import os
import boto3
from boto3.dynamodb.conditions import Key

# Globals
notes_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')

def list_notes(event):
    try:
        user_id = event['requestContext']['authorizer']['claims']['sub'] #verified
        print(f"Extracted user_id: {user_id}")

        table = dynamodb.Table(notes_table)

        # Ensure the query matches the table's key structure
        response = table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )
        # response = user_id

        print(f"DynamoDB Response: {response}")

        user_notes = []
        for items in response['Items']:
            user_notes.append(items)

        return user_notes
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def lambda_handler(event, context):
    try:
        notes = list_notes(event)
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps(
                notes
            )
        }
        return response
    except Exception as err:
        print(f"Unhandled Error: {str(err)}")
        raise
