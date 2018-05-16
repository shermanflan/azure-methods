using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Globalization;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;

using Microsoft.IdentityModel.Clients.ActiveDirectory;
using Newtonsoft.Json;

using AzureOAuthClient.D365.Poco;

namespace AzureOAuthClient.D365.Security.Oauth2
{
    /*
     * Even though this is a desktop application, this is a confidential 
     * client application so Azure Application Type should be Web app / API.
     * 
     * Based on:
     *  1. https://github.com/Azure-Samples/active-directory-dotnet-daemon
     * 
     * Cannot get this to work against a public API (Graph API). "Forbidden"
     * is returned. 
     */
    public class DaemonKeyGraphAPI
    {
        private static AuthenticationContext authContext = null;
        private static ClientCredential clientCredential = null;

        public string Authority { get; set; }
        public string Tenant { get; set; }
        public string ClientId { get; set; }
        public string AppKey { get; set; }

        public string APIResourceId { get; set; } // target API
        public string APIEndpoint { get; set; }

        public DaemonKeyGraphAPI(string authority, string tenant, string client, string appKey
                                , string resource, string apiEndpoint)
        {
            Debug.Listeners.Add(new TextWriterTraceListener(Console.Out));
            Debug.AutoFlush = true;

            Authority = authority;
            Tenant = tenant;
            ClientId = client;
            AppKey = appKey;
            APIResourceId = resource;
            APIEndpoint = apiEndpoint;

            InitializeContext();
        }

        // TODO: Refactor to Oauth2 class.
        private void InitializeContext()
        {
            // Pass ADAL the coordinates it needs to communicate with Azure AD and tell it how to cache tokens.
            // TODO: Maybe a different way to build context?
            // Address validation off? https://docs.microsoft.com/en-us/dotnet/api/microsoft.identitymodel.clients.activedirectory.authenticationcontext.-ctor?view=azure-dotnet#Microsoft_IdentityModel_Clients_ActiveDirectory_AuthenticationContext__ctor_System_String_System_Boolean_
            authContext = new AuthenticationContext(Authority);

            // TODO: Maybe a different way to build credential?
            clientCredential = new ClientCredential(ClientId, AppKey);
        }

        // TODO: Refactor to Oauth2 class.
        // TODO: Add retry logic.
        public async Task<AuthenticationResult> AcquireToken()
        {
            // Get an access token from Azure AD using client credentials.
            AuthenticationResult result = null;
            try
            {
                // ADAL includes an in memory cache, so this call will only send a message to the server if the 
                // cached token is expired.
                // TODO: Maybe a different way to acquire token?
                result = await authContext.AcquireTokenAsync(
                                                APIResourceId,
                                                clientCredential
                                            );

                Debug.WriteLine("Acquired token via app key.");
                return result;
            }
            catch (AdalException ex)
            {
                if (ex.ErrorCode != AdalError.FailedToAcquireTokenSilently
                    && ex.ErrorCode != AdalError.InteractionRequired)
                {
                    throw ex;
                }
            }

            return result;
        }

        // Invoke API
        public void PostTodo()
        {
            //
            // Get an access token from Azure AD using client credentials.
            // If the attempt to get a token fails because the server is unavailable, retry twice after 3 seconds each.
            //
            AuthenticationResult result = AcquireToken().Result;

            //
            // Post an item to the To Do list service.
            //

            // Add the access token to the authorization header of the request.
            HttpClient httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

            // Forms encode To Do item and POST to the todo list web api.
            string timeNow = DateTime.Now.ToString();
            Console.WriteLine("Posting to To Do list at {0}", timeNow);
            string todoText = "RKO Task at time: " + timeNow;
            HttpContent content = new FormUrlEncodedContent(new[] { new KeyValuePair<string, string>("Title", todoText) });
            HttpResponseMessage response = httpClient.PostAsync(APIEndpoint + "/api/todolist", content).Result;

            if (response.IsSuccessStatusCode == true)
            {
                Console.WriteLine("Successfully posted new To Do item:  {0}\n", todoText);
            }
            else
            {
                Console.WriteLine("Failed to post a new To Do item\nError:  {0}\n", response.ReasonPhrase);
            }
        }

        public string GetUser(string prefix)
        {
            // Get an Access Token for the Graph API
            AuthenticationResult result = AcquireToken().Result;

            // Once we have an access_token, invoke API.
            // Call the To Do list service.
            Console.WriteLine("Retrieving To Do list at {0}", DateTime.Now.ToString());
            HttpClient httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);
            HttpResponseMessage response = httpClient.GetAsync(APIEndpoint + "/api/todolist").Result;

            StringBuilder todo = new StringBuilder();
            if (response.IsSuccessStatusCode)
            {
                // Read the response and output it to the console.
                string content = response.Content.ReadAsStringAsync().Result;

                try
                {
                    var inputJson = JsonConvert.DeserializeObject<List<TodoItem>>(content);

                    foreach (var t in inputJson)
                    {
                        todo.AppendLine(t.ToString());
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine(e.ToString());
                    throw;
                }
            }
            else
            {
                Console.WriteLine("Failed to retrieve To Do list\nError:  {0}\n", response.ReasonPhrase);
            }

            return todo.ToString();
        }
        /*
        public string WhoAmI()
        {
            // Get an Access Token for the Graph API
            AuthenticationResult result = AcquireToken(GraphResourceId, ClientId, RedirectUri).Result;

            // Once we have an access_token, invoke API.
            string graphRequest = String.Format(CultureInfo.InvariantCulture
                                    , "{0}me"
                                    , GraphApiEndpoint);
            HttpRequestMessage request = new HttpRequestMessage(HttpMethod.Get, graphRequest);

            // Oauth2 Access Token
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

            HttpClient httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("api-version", GraphApiVersion);
            HttpResponseMessage response = httpClient.SendAsync(request).Result;

            if (!response.IsSuccessStatusCode)
            {
                throw new WebException(response.StatusCode.ToString() + ": " + response.ReasonPhrase);
            }

            string content = response.Content.ReadAsStringAsync().Result;
            JObject jResult = JObject.Parse(content);

            if (jResult["odata.error"] != null)
            {
                throw new Exception((string)jResult["odata.error"]["message"]["value"]);
            }

            return String.Format($"{jResult["givenName"]} {jResult["surname"]}");
        }
        */
    }
}
