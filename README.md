# EasyNote
Serverless Note Taking Application built using Blazor WebAssembly (FrontEnd) and AWS SAM template (BackEnd). User can Login/Register and can perform CRUD operations with notes. Notes can also be categorised.

The site can be visited here: https://eznoteapp.netlify.app/ 

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


# Project Structure

# BackEnd
As stated previously, the backend has been powered by AWS SAM. We make two AWS SAM templates for the backend, so that we can define the resources needed to Create, Save and Update Users for Authorisation Purposes as well as the resources needed so that users can manipulate Notes.

<img src="./aws chart (1).png" title="architectural overview of BackEnd">

## USERS AND NOTES
Both the Users and Notes AWS SAM template define the resources required for to enable Users Authorisation and manipulation. Below are the defined microservices in both tables. 

1) Users Table - Database where the Users information is stored.
2) Users Lambda Function - One monolithic lambda dunction to handle user operations - CRUD User Function.
3) Users API Gateway - Gateway for Client to Interact with Lambda function which manipulate Database.

## AUTHORISATION and USERPOOL

For the purposes of authorisation a Cognito Userpool is created which defines the pool of users who can access a resource.

Both the Users and Notes API Gateway's which provide users with access to functions to manipulate the database, and secured by an Authorizer which is connected to the Userpool.

Therefore, this ensures that only authorised users who are part of the userpool can manipulate user and note data.

# FrontEnd

## AUTHORISATION - LOGIN AND REGISTRATION PAGES

For registering new users and logging in, we have 2 seperate pages. The pages have forms, whose inputs perform asynchronous tasks for logging in and registering.
The Amazon CognitoIdenityProviderClient class, provides us with the necessary methods to manipulate a userpool and verify user details. This is declared and used in a Seperate Service called `AuthService`. 
Cognito has also been setup such that email verifications are necessary to create accounts, adding another Layer of Security.

FLOWCHART

## NOTES PAGE

In the Home Page, We can Interact with the API for Notes by making asynchronous called to the NotesService, which perform HTTP called to our Notes API. We can Create Notes, Edit Notes, Delete Notes and View all Notes.


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




------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
