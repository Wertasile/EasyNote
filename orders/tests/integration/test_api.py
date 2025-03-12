import json
import requests
import logging
import time
import uuid
import pytest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

note_1 = {
    "noteContent": "My first note",
    "noteId": str(uuid.uuid4()),
    "noteTitle" : "My first Title",
    "noteCategory": "Random",
    "status": "PLACED"
}

# GLOBAL VARAIBLES FOR NOTES ENDPOINT
@pytest.fixture
def notes_endpoint(global_config):
  '''Returns the endpoint for the Notes service'''
  notes_endpoint = global_config["NotesServiceEndpoint"] + '/notes'
  logger.debug("Notes Endpoint = " + notes_endpoint)
  return notes_endpoint

# GLOBAL VARAIBLES FOR USER TOKEN FOR AUTHORIZATION
@pytest.fixture
def user_token(global_config):
  '''Returns the user_token for authentication to the Notes service'''
  user_token = global_config["user1UserIdToken"]
  logger.debug("     User Token = " + user_token)
  return user_token

# TEST 1
@pytest.mark.order(1)
def test_access_notes_without_authentication(notes_endpoint):
  response = requests.post(notes_endpoint)
  assert response.status_code == 401

# TEST 2
@pytest.mark.order(2)
def test_add_new_note(global_config, notes_endpoint, user_token):
  response = requests.post(notes_endpoint, data=json.dumps(note_1),
      headers={'Authorization': user_token, 'Content-Type': 'application/json'}
      )
  logger.debug("Add new note response: %s", response.text)
  assert response.status_code == 200
  note_info = response.json()
  note_id = note_info['noteId']
  note_time = note_info['noteTime']
  logger.debug("New noteId: %s", note_id)
  global_config['noteId'] = note_id
  global_config['noteTime'] = note_time
  assert note_info['status'] == "PLACED"
  logger.info("Global config after test 2: %s", global_config)
  print("Global config after test 2:", global_config)


# TEST 3
@pytest.mark.order(3)
def test_get_note(global_config, notes_endpoint, user_token):
  
  response = requests.get(notes_endpoint + "/" + global_config['noteId'],
      headers={'Authorization': user_token, 'Content-Type': 'application/json'}
      )

  logger.debug(response.text)
  note_info = json.loads(response.text)
  # assert note_info['noteId'] == global_config['noteId']
  # assert note_info['status'] == "PLACED"
  # assert note_info['noteContent'] == "My first note"
  assert note_info['noteTitle'] == "My first Title"
  # assert note_info['noteCategory'] == "Random"
# Add your API integration testing code here