using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using System;
using System.Net.Http;
using System.Threading.Tasks;
using Blazored.LocalStorage;
using AWS_SAM_Note_App_FrontEnd;


var builder = WebAssemblyHostBuilder.CreateDefault(args);

builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

//Console.WriteLine("Configuring Services...");

// 1. ---- Register Local Storage ---------
builder.Services.AddBlazoredLocalStorage();
Console.WriteLine("✅ BlazoredLocalStorage Registered!");

// 2. ---- Register HTTP Client ----
builder.Services.AddScoped<HttpClient>(sp =>
{
    Console.WriteLine("Registering HttpClient...");

    var client = new HttpClient { BaseAddress = new Uri("https://6yfkr7gn38.execute-api.us-east-1.amazonaws.com/Prod/") };

    _ = Task.Run(async () =>
    {
        try
        {
            var localStorage = sp.GetRequiredService<ILocalStorageService>();
            var token = await localStorage.GetItemAsync<string>("id_token");

            if (!string.IsNullOrEmpty(token))
            {
                client.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);
                Console.WriteLine($"Token Added to HttpClient Headers: {token}");
            }
            else
            {
                Console.WriteLine("No Token Found - HttpClient will not have Authorization header.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error retrieving token: {ex.Message}");
        }
    });
    Console.WriteLine("HttpClient Registered!");
    return client;
});


// Register NotesService
builder.Services.AddScoped<NotesService>(sp =>
{
    Console.WriteLine("Registering NotesService...");
    try
    {
        var localStorage = sp.GetRequiredService<ILocalStorageService>();
        var httpClient = sp.GetRequiredService<HttpClient>(); // Ensure HttpClient is resolved
        Console.WriteLine("✅ NotesService Registered Successfully!");
        return new NotesService(httpClient, localStorage);
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error registering NotesService: {ex.Message}");
        throw;
    }
});

// Register AuthService
builder.Services.AddScoped<AuthService>();
builder.Services.AddScoped<UserService>();
builder.Services.AddScoped<NoteState>();
Console.WriteLine("✅ AuthService Registered!");

Console.WriteLine("Starting Application...");
await builder.Build().RunAsync();
Console.WriteLine("✅ Application started!");
