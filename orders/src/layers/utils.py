from boto3.dynamodb.conditions import Key
import boto3
import os

notes_table = os.getenv('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')

def get_note(user_id, note_id):
    table = dynamodb.Table(notes_table)
    response = table.query(
        KeyConditionExpression=(Key('userId').eq(user_id) & Key('noteId').eq(note_id))
    )
    
    # below is the api response
    if response['Items']:
        note = response['Items'][0]
        print(f"Note Title: {note['noteTitle']}")
        return note
    else:
        print("No note found")
        return None
    # user_notes = []
    # for item in response['Items']:
    #   user_notes.append(item['noteTitle'])
    #   user_notes.append(item['noteContent'])
    #   user_notes.append(item['noteCategory'])
    #   user_notes.append(item['status'])
    #   user_notes.append(item['noteTime'])
      
      
    # if user_notes:
    #     print(user_notes[0])
    #     return user_notes[0:5]
    # else:
    #     print("No note found")
    #     return None