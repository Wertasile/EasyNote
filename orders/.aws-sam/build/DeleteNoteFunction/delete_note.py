import simplejson as json
import os
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# Load DynamoDB Table Name from environment variables
notes_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')

def delete_note(event, context):
    """Deletes a note from DynamoDB based on userId and noteId"""
    try:
        # Extract userId and noteId from the request
        user_id = event['requestContext']['authorizer']['claims']['sub']
        note_id = event['pathParameters']['noteId']

        table = dynamodb.Table(notes_table)
        
        # Perform the deletion
        response = table.delete_item(
            Key={'userId': user_id, 'noteId': note_id},
            ConditionExpression="attribute_exists(noteId)"  # Prevent deleting non-existent notes
        )
        return {"message": "Note deleted successfully"}
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {"error": "Note not found"}
        else:
            print(f"Unexpected error: {e}")
            return {"error": "Internal server error"}

def lambda_handler(event, context):
    try:
        result = delete_note(event, context)
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"},
            "body": json.dumps(result)
        }
    except Exception as err:
        print(f"Error in lambda_handler: {err}")
        return {
            "statusCode": 500,
            "headers": {},
            "body": json.dumps({"error": "Something went wrong"})
        }
