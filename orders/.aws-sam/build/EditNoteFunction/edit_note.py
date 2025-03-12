import simplejson as json
import os  # used to fetch environment variables
import boto3 # aws sdk for python to interact with DynamoDB
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal import Decimal
from utils import get_note

# Globals
note_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')

def edit_note(event):
    # get username from the JWT token
    user_id = event['requestContext']['authorizer']['claims']['sub'] 

    # get noteid from the path url
    note_id = event['pathParameters']['noteId']

    new_data = json.loads(event['body'], parse_float=Decimal) # loads content from request, has category, title, content, etc but not user id and note id 
    
    # we are now extracting note values from the response dictionary
    
    note_title = new_data.get('noteTitle')
    note_content = new_data.get('noteContent')
    note_category = new_data.get('noteCategory')
    note_time = new_data.get('noteTime')

    # extracted values are then put in the response update dictionary
    ddb_item = {
                'noteId': note_id,
                'userId': user_id,
                'noteTitle': note_title,
                'noteContent': note_content,
                'noteCategory': note_category,
                'noteTime': note_time,
                'status': "PLACED"
            }
    
    ddb_item = json.loads(json.dumps(ddb_item), parse_float=Decimal)

    table = dynamodb.Table(note_table)
    try:
        table.put_item(
            Item=ddb_item, 
            # ConditionExpression="attribute_exists(noteId) AND attribute_exists(userId) AND #data.#status = :status",
            # ExpressionAttributeNames={
            #     "#data": "data",
            #     "#status": "status"
            # },
            # ExpressionAttributeValues={
            #     ":status": "PLACED"
            # },
            # ReturnValuesOnConditionCheckFailure="ALL_OLD"
        )
    except ClientError as exc:
        if exc.response['Error']['Code'] == 'ConditionalCheckFailedException':
            raise Exception(f"Cannot edit Note {note_id}. Please check if the note exists and the status is PLACED.")
        else:
            raise Exception
        (f"Error occurred: {exc.response['Error']['Code']}: {exc.response['Error']['Message']}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")

    return get_note(user_id, note_id)


def lambda_handler(event, context):
    try:
        updated = edit_note(event)
        response = {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"},
            "body": json.dumps(updated)
        }
        return response
    except Exception as err:
        raise Exception(str(err))

