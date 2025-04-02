using Amazon.CognitoIdentityProvider;
using Amazon.CognitoIdentityProvider.Model;
using Amazon.Runtime;
using Blazored.LocalStorage;
using System.Text.Json;
using System.Text;
using System.IdentityModel.Tokens.Jwt;
using System.Net.Http.Json;

public class UserService
{
    private readonly HttpClient _httpClient;

    private readonly string _clientId = "700qvc6ddlmi3dd2s7a09f8k4v"; // Update with the actual Cognito User Pool Client ID
    private readonly AmazonCognitoIdentityProviderClient _cognitoClient;

    private readonly ILocalStorageService _localStorage;  // added for local storage

    private const string ApiUrl = "https://xnxwxuh5l1.execute-api.us-east-1.amazonaws.com/Prod/users"; // Replace with actual API Gateway URL


    public UserService(HttpClient httpClient, ILocalStorageService localStorage)
    {
        Console.WriteLine("UserService is being created...");
        _cognitoClient = new AmazonCognitoIdentityProviderClient(new AnonymousAWSCredentials(), Amazon.RegionEndpoint.USEast1); // Adjust the region
        _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
        _localStorage = localStorage ?? throw new ArgumentNullException(nameof(localStorage)); // added for local storage
    }

    // seperate function to get tokens

    private async Task<string> GetIdTokenAsync()
    {
        var token = await _localStorage.GetItemAsync<string>("id_token");
        return token;
    }

    private async Task<string> GetAccessTokenAsync()
    {
        var accesstoken = await _localStorage.GetItemAsync<string>("access_token");
        return accesstoken;
    }

    // seperate function to set header for api request after obtaining token

    public async Task SetAuthorizationHeaderAsync()
    {
        var token = await GetIdTokenAsync();
        if (!string.IsNullOrEmpty(token))
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);
        }
    }

    //To get the user ID via access token, which then gets saved to local storage in frontend

    public async Task<string> GetUserIdAsync()
    {
        var accessToken = await GetAccessTokenAsync();
        try
        {
            var request = new GetUserRequest
            {
                AccessToken = accessToken
            };

            var userResponse = await _cognitoClient.GetUserAsync(request);
            Console.WriteLine($"✅ Retrieved User ID: {userResponse.Username}");

            return userResponse.Username;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error fetching User ID: {ex.Message}");
            return "Error";
        }
    }

    // --------------------------------------- API CALLS ------------------------------------------------------

    // create user is register user and is not called here, it is called in Auth service under RegisterUser async task

    // GET USER DETAILS.
    public async Task<User> GetUserDetailsAsync()
    {
        var userid = await _localStorage.GetItemAsStringAsync("user_id");
        Console.WriteLine("GETTING USERID IN USERSERVICE" + userid);
        await SetAuthorizationHeaderAsync();
        return await _httpClient.GetFromJsonAsync<User>($"{ApiUrl}/{userid}");

    }

    // EDIT USER DETAILS.

    // DELETE USER.



}
