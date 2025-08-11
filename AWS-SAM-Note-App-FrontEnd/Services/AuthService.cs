using Amazon.CognitoIdentityProvider;
using Amazon.CognitoIdentityProvider.Model;
using Amazon.Runtime;
using Blazored.LocalStorage;
using System.Text.Json;
using System.Text;
using System.IdentityModel.Tokens.Jwt;


public class AuthService
{
    private readonly string _clientId = "700qvc6ddlmi3dd2s7a09f8k4v"; // Update with the actual Cognito User Pool Client ID
    private readonly AmazonCognitoIdentityProviderClient _cognitoClient;
    private readonly ILocalStorageService _localStorage;

    private readonly HttpClient _httpClient;

    public AuthService(HttpClient httpClient, ILocalStorageService localStorage)
    {
        _cognitoClient = new AmazonCognitoIdentityProviderClient(new AnonymousAWSCredentials(), Amazon.RegionEndpoint.USEast1); // Adjust the region
        _httpClient = httpClient;
        _localStorage = localStorage;
    }

    // creating new user where we the use the POST request described in AWS SAM template
    public async Task<bool> RegisterUser(string username, string password, string email)
    {
        var payload = new
        {
            name = username,
            username = email,
            password = password,
            email = email
        };

        var content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync("https://xnxwxuh5l1.execute-api.us-east-1.amazonaws.com/Prod/users", content);

        return response.IsSuccessStatusCode;
    }


    // Confirm Sign-Up (User enters a code sent to their email)
    public async Task<bool> ConfirmSignUpAsync(string username, string confirmationCode)
    {
        try
        {
            var request = new ConfirmSignUpRequest
            {
                ClientId = _clientId,
                Username = username,
                ConfirmationCode = confirmationCode
            };

            var response = await _cognitoClient.ConfirmSignUpAsync(request);
            return response.HttpStatusCode == System.Net.HttpStatusCode.OK;
        }
        catch (CodeMismatchException)
        {
            throw new Exception("Invalid confirmation code. Please try again.");
        }
        catch (ExpiredCodeException)
        {
            throw new Exception("Confirmation code has expired. Request a new one.");
        }
        catch (Exception ex)
        {
            throw new Exception($"Error confirming sign-up: {ex.Message}");
        }
    }

    // Resend Confirmation Code (if the user didn't receive it)
    public async Task<string> ResendConfirmationCodeAsync(string username)
    {
        try
        {
            var request = new ResendConfirmationCodeRequest
            {
                ClientId = _clientId,
                Username = username
            };

            var response = await _cognitoClient.ResendConfirmationCodeAsync(request);
            return "A new confirmation code has been sent to your registered email.";
        }
        catch (Exception ex)
        {
            throw new Exception($"Error resending confirmation code: {ex.Message}");
        }
    }

    public async Task<Dictionary<String, String>> SignInAsync(string username, string password)
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
        Console.WriteLine(authResponse.AuthenticationResult.IdToken.ToString());
        var id_token = authResponse.AuthenticationResult.IdToken.ToString();
        var access_token = authResponse.AuthenticationResult.AccessToken.ToString();


        var tokens = new Dictionary<string, string>{
            {"id_token",id_token},
            {"access_token",access_token},
        };
        return tokens;
        // we return the access token

    }


}


