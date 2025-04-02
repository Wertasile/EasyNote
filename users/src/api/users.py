# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import uuid
import os
import boto3
from datetime import datetime

# Initialize AWS Clients
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
USERS_TABLE = os.getenv('USERS_TABLE')

cognito = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')
ddbTable = dynamodb.Table(USERS_TABLE)

def lambda_handler(event, context):
    route_key = f"{event['httpMethod']} {event['resource']}"

    # Set default response, override with data from DynamoDB if any
    response_body = {'Message': 'Unsupported route'}
    status_code = 400
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }

    try:
        # Get a list of all Users
        if route_key == 'GET /users':
            ddb_response = ddbTable.scan(Select='ALL_ATTRIBUTES')
            # return list of items instead of full DynamoDB response
            response_body = ddb_response['Items']
            status_code = 200

        # CRUD operations for a single User
       
        # Read a user by accessToken
        if route_key == 'GET /users/{userid}':
            # get data from the database
            ddb_response = ddbTable.get_item(
                Key={'userid': event['pathParameters']['userid']}
            )
            # return single item instead of full DynamoDB response
            if 'Item' in ddb_response:
                response_body = ddb_response['Item']
            else:
                response_body = {}


            status_code = 200
        
        # Delete a user by ID
        if route_key == 'DELETE /users/{userid}':
            # delete item in the database
            ddbTable.delete_item(
                Key={'userid': event['pathParameters']['userid']}
            )
            response_body = {}
            status_code = 200
        
        # Create a new user 
        if route_key == 'POST /users':
            request_json = json.loads(event['body'])
            request_json['timestamp'] = datetime.now().isoformat()
            # generate unique id if it isn't present in the request
            if 'userid' not in request_json:
                request_json['userid'] = str(uuid.uuid1())
            name = request_json.get('name')
            username = request_json.get('username')
            email = request_json.get('email')
            password = request_json.get('password')
            
            # Step 1: Create Cognito User
            response = cognito.sign_up(
                ClientId=CLIENT_ID,
                Username=username,
                Password=password,
                UserAttributes=[{'Name': 'email', 'Value': email},{'Name':'name','Value':name}]
            )

            user_sub = response['UserSub']  # Cognito user ID (UUID)
            
            # Step 2: Store in DynamoDB
            user_item = {
                'userid': user_sub,  # Store Cognito User ID as partition key
                'username': username,
                'email': email,
                'created_at': datetime.now().isoformat()
            }
            ddbTable.put_item(Item=user_item)

            response_body = {'Message': 'User registered successfully', 'userid': user_sub}
            status_code = 200

        # Update a specific user by ID
        if route_key == 'PUT /users/{userid}':
            # update item in the database
            request_json = json.loads(event['body'])
            request_json['timestamp'] = datetime.now().isoformat()
            request_json['userid'] = event['pathParameters']['userid']
            # update the database
            ddbTable.put_item(
                Item=request_json
            )
            response_body = request_json
            status_code = 200

        if route_key == 'OPTIONS /users':
            response_body = request_json
            status_code = 200
            
    except Exception as err:
        status_code = 400
        response_body = {'Error:': str(err)}
        print(str(err))
    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }