
using System.Net.Http.Json;
using Blazored.LocalStorage;

public class NotesService
{
    private readonly HttpClient _httpClient;

    private readonly ILocalStorageService _localStorage;  // added for local storage

    private const string ApiUrl = "https://6yfkr7gn38.execute-api.us-east-1.amazonaws.com/Prod/notes"; // Replace with actual API Gateway URL

    public NotesService(HttpClient httpClient, ILocalStorageService localStorage)
    {
        Console.WriteLine("NotesService is being created...");
        _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
        _localStorage = localStorage ?? throw new ArgumentNullException(nameof(localStorage)); // added for local storage
    }

    // seperate function to get token

    private async Task<string> GetIdTokenAsync()
    {
        var token = await _localStorage.GetItemAsync<string>("id_token");
        return token;
    }

    // seperate function to set header for api request after obtaining token

    private async Task SetAuthorizationHeaderAsync()
    {
        var token = await GetIdTokenAsync();
        if (!string.IsNullOrEmpty(token))
        {
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);
        }
    }

    //gettting notes upon loading in

    public async Task<List<Note>> GetNotesAsync()
    {
        await SetAuthorizationHeaderAsync();
        return await _httpClient.GetFromJsonAsync<List<Note>>(ApiUrl) ?? new List<Note>();
    }

    // getting a note by an ID

    public async Task<List<Note>> GetNoteByIdAsync(string id)
    {
        await SetAuthorizationHeaderAsync();
        return await _httpClient.GetFromJsonAsync<List<Note>>($"{ApiUrl}/{id}");
    }

    // adding a note

    public async Task AddNoteAsync(Note note)
    {
        await SetAuthorizationHeaderAsync();
        await _httpClient.PostAsJsonAsync(ApiUrl, note);
    }

    // updating a note

    public async Task UpdateNoteAsync(Note note)
    {
        await SetAuthorizationHeaderAsync();
        await _httpClient.PutAsJsonAsync($"{ApiUrl}/{note.NoteId}", note);
    }

    // deleting a note

    public async Task DeleteNoteAsync(string noteId)
    {
        await SetAuthorizationHeaderAsync();
        await _httpClient.DeleteAsync($"{ApiUrl}/{noteId}");
    }
}
