using Amazon.CognitoIdentityProvider;
using Amazon.CognitoIdentityProvider.Model;
using Amazon.Runtime;
using System;
using System.Threading.Tasks;


public class AuthService
{
    private readonly string _clientId = "700qvc6ddlmi3dd2s7a09f8k4v"; // Update with the actual Cognito User Pool Client ID
    private readonly AmazonCognitoIdentityProviderClient _cognitoClient;

    public AuthService()
    {
        _cognitoClient = new AmazonCognitoIdentityProviderClient(new AnonymousAWSCredentials(), Amazon.RegionEndpoint.USEast1); // Adjust the region
    }

    public async Task<string> SignUpAsync(string username, string password, string email)
    {
        var signUpRequest = new SignUpRequest
        {
            ClientId = _clientId,
            Username = username,
            Password = password,
            UserAttributes = new List<AttributeType>
            {
                new AttributeType { Name = "email", Value = email }
            }
        };

        var signUpResponse = await _cognitoClient.SignUpAsync(signUpRequest);

        return signUpResponse.UserSub;
    }

    public async Task<string> SignInAsync(string username, string password)
    {
        var authRequest = new InitiateAuthRequest
        {
            AuthFlow = AuthFlowType.USER_PASSWORD_AUTH,     // select the authentication type
            ClientId = _clientId,                           // put in the cognito client ID
            AuthParameters = new Dictionary<string, string> // we create a dictionary to store username (email) and password
            {
                { "USERNAME", username },
                { "PASSWORD", password }
            }
        };

        var authResponse = await _cognitoClient.InitiateAuthAsync(authRequest);

        return authResponse.AuthenticationResult.IdToken;   // we return the access token

        
    }

    // public async Task SignOutAsync()
    // {
    //     // Handle sign-out (clear tokens, etc.)
    // }
}


