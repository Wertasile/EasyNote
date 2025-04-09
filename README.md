# EasyNote
Serverless Note Taking Application built using Blazor WebAssembly (FrontEnd) and AWS SAM template (BackEnd). User can Login/Register and can perform CRUD operations with notes. Notes can also be categorised.

The site can be visited here: http://awssamnoteapp.s3-website-us-east-1.amazonaws.com 

<i> Update: At its current stage, the backend infrastrucutre is fully deployed however the frontend is still in development. </i>

# Introduction
The main objective of this project, was to make use of AWS SAM (Serverless Application Model) to build and deploy serverless applications. 

We build AWS SAM templates which enable us to define Infrastructure as Code (IaC). The AWS SAM CLI (Command Line Interface) is then used to deploy and manage the serverless application. 

This application mainly consists of the following 4 AWS Services for the BackEnd Infrastructure.
1) API Gateway - REST API so that user can interact with Data
2) Lambda - Functions to Add, Edit, View and Retrieve Data
3) Cognito - To secure the app and manage access (LogIn and Registration)
4) DynamoDB - To store Data

The FrontEnd of the application (User Interface) is built using Blazor WebAssembly (C# .NET7).


# History and References

# Project Structure


# BackEnd
As stated previously, the backend has been powered by AWS SAM. We make two AWS SAM templates for the backend, so that we can define the resources needed to Create, Save and Update Users for Authorisation Purposes as well as the resources needed so that users can manipulate Notes.

## Authorisation and Users
We create a microservice to add and update user accounts. The following steps are required to do this. The template file to perform this can be found here : 

1) Firstly, we need to create a database where the Users information is stored.
2) After that, we will need to define the logic (Lambda Function). We will create one monolithic lambda dunction to handle user operations.
3) We then need to define an API, so that the deployed Lambda Functions can interact with Users.
4) We then need to create an Amazon Cognito Userpool, 

All of the above services are created under the ``` users ``` directory. The required services are declared and made via an AWS SAM template.



### DEFINING A TABLE FOR USERS

We first need to define a Data Structure for the users, and create a table to store user data. All the user has is a userid, which will later be linked to the user email and password.
```
Resources:
    UsersTable:
        Type: AWS::DynamoDB::Table
        Properties:
        TableName: !Sub ${AWS::StackName}-Users
        AttributeDefinitions:
            - AttributeName: userid
            AttributeType: S
        KeySchema:
            - AttributeName: userid
            KeyType: HASH
        BillingMode: PAY_PER_REQUEST

Outputs:
  UsersTable:
    Description: DynamoDB Users table
    Value: !Ref UsersTable
```

### ADDING A LAMBDA FUNCTION
We will create a multi-purpose lambda function to handle several HTTP methods (monolithic function). For the Notes itself, we use serveral single purpose functions for each HTTP method. 

1) We define a Lambda Function resource in the AWS SAM template

A Lambda function resource is defined, with the function itself located in the src/api/users folder. The function itself is called lambda_handler.

```
UsersFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/api/users.lambda_handler
      Description: Handler for all users related operations
      Environment:
        Variables:
          USERS_TABLE: !Ref UsersTable
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable
      Tags:
        Stack: !Sub "${AWS::StackName}"
      Events:
        GetUsersEvent:
          Type: Api
          Properties:
            Path: /users
            Method: get
            RestApiId: !Ref RestAPI
        PutUserEvent:
          Type: Api
          Properties:
            Path: /users
            Method: post
            RestApiId: !Ref RestAPI
        UpdateUserEvent:
          Type: Api
          Properties:
            Path: /users/{userid}
            Method: put
            RestApiId: !Ref RestAPI
        GetUserEvent:
          Type: Api
          Properties:
            Path: /users/{userid}
            Method: get
            RestApiId: !Ref RestAPI
        DeleteUserEvent:
          Type: Api
          Properties:
            Path: /users/{userid}
            Method: delete
            RestApiId: !Ref RestAPI
```

2) We create the Lambda Function itself.

The function is defined in users.py, where based on the type of request we get, a different response and action is performed on the DynamoDB table.

```
USERS_TABLE = os.getenv('USERS_TABLE', None)
dynamodb = boto3.resource('dynamodb')
ddbTable = dynamodb.Table(USERS_TABLE)

def lambda_handler(event, context):
    route_key = f"{event['httpMethod']} {event['resource']}"

    # Set default response, override with data from DynamoDB if any
    response_body = {'Message': 'Unsupported route'}
    status_code = 400
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
        }

    try:
        # Get a list of all Users
        if route_key == 'GET /users':
            ddb_response = ddbTable.scan(Select='ALL_ATTRIBUTES')
            # return list of items instead of full DynamoDB response
            response_body = ddb_response['Items']
            status_code = 200

        # CRUD operations for a single User
       
        # Read a user by ID
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
            # update the database
            ddbTable.put_item(
                Item=request_json
            )
            response_body = request_json
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
    except Exception as err:
        status_code = 400
        response_body = {'Error:': str(err)}
        print(str(err))
    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }
```

### CREATING AN API
Nextly, we will need to define a REST API, which acts as the frontdoor, to ensure that users can access the above defined functions. Now, each request to the API endpoint will invoke UsersFunction (This is the AWS Lamda function resource defined previously, which performs code in ``/src/api/users`` and the function ``lambda_handler``).

```
RestAPI:
    Type: AWS::Serverless::Api
    Properties:
      StageName: Prod
      TracingEnabled: true
      Tags:
        Name: !Sub "${AWS::StackName}-API"
        Stack: !Sub "${AWS::StackName}"  
```

### CREATING COGNITO USER POOL AND AUTHORIZER FUNCTION
To ensure that only authorized users can get access to the users API Gateway and perform the relevant functions, we create a Lambda Authoriser function called ```src/api/authorizer.py```.

To refer to these authorized users, we create and define an Amazon Cognito userpool, which contains authorized users in a single pool. Amazon cognito also provide user sign-up, sign-in and access control.

```
  UserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: !Sub ${AWS::StackName}-UserPool
      AdminCreateUserConfig:
        AllowAdminCreateUserOnly: false
      AutoVerifiedAttributes:
        - email
      Schema:
        - Name: name
          AttributeDataType: String
          Mutable: true
          Required: true
        - Name: email
          AttributeDataType: String
          Mutable: true
          Required: true
      UsernameAttributes:
        - email
      UserPoolTags:
        Key: Name
        Value: !Sub ${AWS::StackName} User Pool
```

A Client and Domain also need to be defined in the template. 

```
  UserPoolClient:
    Type: AWS::Cognito::UserPoolClient
    Properties:
      ClientName: !Sub ${AWS::StackName}UserPoolClient
      ExplicitAuthFlows:
        - ALLOW_USER_PASSWORD_AUTH
        - ALLOW_USER_SRP_AUTH
        - ALLOW_REFRESH_TOKEN_AUTH
      GenerateSecret: false
      PreventUserExistenceErrors: ENABLED
      RefreshTokenValidity: 30
      SupportedIdentityProviders:
        - COGNITO
      UserPoolId: !Ref UserPool
      AllowedOAuthFlowsUserPoolClient: true
      AllowedOAuthFlows:
        - "code"
      AllowedOAuthScopes:
        - "email"
        - "openid"
      CallbackURLs:
        - "http://localhost"

  UserPoolDomain:
    Type: AWS::Cognito::UserPoolDomain
    Properties:
      Domain: !Ref UserPoolClient
      UserPoolId: !Ref UserPool
```

We also create a Group within the UserPool, for users who have administrative permissions.
```
  ApiAdministratorsUserPoolGroup:
    Type: AWS::Cognito::UserPoolGroup
    Properties:
      Description: User group for API Administrators
      GroupName: !Ref UserPoolAdminGroupName
      Precedence: 0
      UserPoolId: !Ref UserPool
```

We, then create the Authoriser Function to secure the API,



## Notes


# FrontEnd

# Connecting AWS BackEnd and Blazor FrontEnd

# Result

# Issues Faced.

When users were logging in and signing up, these were done via Cognito API functions and these users were saved in the UserPool that was defined in the AWS template.
However, these users were not being saved in the DynamoDB Table, which were being manipulated by the API calls. 

Therefore, the DynamoDB had a standalone list of users, and since user logging in/ registration in FrontEnd was being managed by Cognito API directly and not API calls, Cognito User Pool users and DynamoDB users were seperate.

TLDR: DynamoDB table and UserPool were not linked. API calls manipulated only <b>DynamoDB table</b> but were not in user.

<b>SOLUTION</b> : Make user use API calls instead of cognito API functions and perform DynamoDB manipulation and Cognito user pool manipulation within API call. Both were not being updated with the information and the same time and are in Sync.

# Others

Potential Upcoming features:
- Calendar and Event Integration.
- Text-to-Speech
- Embedding and saving voice memos.
- Embedding Images and other Files.
- Scratch pad, to draw and scribble.
- Customise notes i.e, colours, fonts, sizing, etc.
- Sharing Notes

Current Features:
- Users can create, read, update and delete notes.
- Users can login/ register to save notes.
- Notes can be categorised.


