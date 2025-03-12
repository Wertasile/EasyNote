import simplejson as json
from utils import get_note


def lambda_handler(event, context):
    user_id = event['requestContext']['authorizer']['claims']['sub']
    note_id = event['pathParameters']['noteId']                           # note_id is extracted from pathparameter of URL

    try:
        notes = get_note(user_id, note_id)
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps(notes)
        }
        return response  # body that is returned
    except Exception as err:
        raise