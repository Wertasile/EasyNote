import os
import boto3
from decimal import Decimal
import json
import uuid
from datetime import datetime

# Globals
notes_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')

def add_note(event: dict):
    detail = json.loads(event['body'])
    note_content = detail['noteContent']
    note_title = detail['noteTitle']
    note_category = detail['noteCategory']
    user_id = event['requestContext']['authorizer']['claims']['sub']
    note_time = datetime.strftime(datetime.utcnow(), '%Y-%m-%dT%H:%M:%SZ')
    note_id = detail['noteId']

    ddb_item = {
        'noteId': note_id,
        'userId': user_id,
        'noteContent': note_content,
        'noteTitle': note_title,
        'noteCategory': note_category,
        'status': 'PLACED',
        'noteTime': note_time,
    }
    ddb_item = json.loads(json.dumps(ddb_item), parse_float=Decimal)

    table = dynamodb.Table(notes_table)
    # We must use conditional expression, otherwise put_item will always replace the original note and will never fail
    table.put_item(Item=ddb_item, ConditionExpression='attribute_not_exists(noteId) AND attribute_not_exists(userId)')

    # this is just for returning
    detail['noteId'] = note_id
    detail['noteTime'] = note_time
    detail['status'] = 'PLACED'

    return detail


def lambda_handler(event, context):
    """Handles the lambda method invocation"""
    try:
        note_detail = add_note(event)
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps(note_detail)
        }
        return response  # body that is returned
    except Exception as err:
        raise
