using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Globalization;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;

using Microsoft.IdentityModel.Clients.ActiveDirectory;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

using UltiSecLib.Azure.OAuth2;

namespace AzureOAuthClient.D365.Security.Oauth2
{
    /*
     * Even though this is a desktop application, this is a confidential 
     * client application so Azure Application Type should be Web app / API.
     * 
     * Successful API calls to AD Graph require the following minimum permissions:
     *  1. Microsoft Graph: Application/Read directory data
     *  2. Microsoft Graph: Delegated/Read directory data
     *  3. Windows Azure Active Directory: Application/Read directory data
     *  4. Windows Azure Active Directory: Delegated/Sign in and read user profile
     * Finally, explict permissions need to be granted (Settings > Required Permissions > Grant Permissions
     * 
     * TODO:
     * - This uses static http client instead of a local instance variable.
     * - Not sure which method is better.
     */
    public class DaemonKeyGraphAPI
    {
        private static HttpClient httpClient = new HttpClient();
        private static IAuthorize authKey = null;

        private static string Authority { get; set; }
        private static string Tenant { get; set; }
        private static string ClientId { get; set; }
        private static string AppKey { get; set; }
        private static string APIResourceId { get; set; } // target API
        private static string APIVersion { get; set; }
        private static string APIEndpoint { get; set; }

        public DaemonKeyGraphAPI(string authority, string tenant, string client, string appKey
                                , string resource, string version, string apiEndpoint)
        {
            Debug.Listeners.Add(new TextWriterTraceListener(Console.Out));
            Debug.AutoFlush = true;

            Authority = authority;
            Tenant = tenant;
            ClientId = client;
            AppKey = appKey;
            APIResourceId = resource;
            APIVersion = version;
            APIEndpoint = apiEndpoint;

            InitializeContext();
        }

        private void InitializeContext()
        {
            authKey = new AuthByAppKey(Authority, Tenant, ClientId, AppKey, APIResourceId);
        }

        // Invoke API
        public static async Task<string> GetUser(string prefix)
        {
            // Get an Access Token for the AD Graph API
            AuthenticationResult result = await authKey.AcquireToken();

            // Once we have an access_token, invoke API.
            httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);
            httpClient.DefaultRequestHeaders.Add("api-version", APIVersion);

            string graphRequest = String.Format(CultureInfo.InvariantCulture
                                                , "{0}{1}/users?$filter=startswith(displayName, '{2}')"
                                                , APIEndpoint, Tenant, prefix);
            HttpResponseMessage response = await httpClient.GetAsync(graphRequest);

            if (response.IsSuccessStatusCode)
            {
                // Read the response and output it to the console.
                string content = await response.Content.ReadAsStringAsync();

                try
                {
                    // TODO: Use canonical JSON deserialization methods.
                    dynamic inputJson = JsonConvert.DeserializeObject(content);
                    var sequence = inputJson["value"];
                    var user1 = sequence[0];

                    return String.Format($"Display Name: {user1["displayName"]}\nMobile: {user1["mobile"]}" +
                                        $"\nUPN: {user1["userPrincipalName"]}\nEmail: {user1["otherMails"][0]}");

                }
                catch (Exception e)
                {
                    Debug.WriteLine(e.ToString());
                    throw;
                }
            }
            else
            {
                throw new InvalidOperationException($"Failed to access API:  {response.ReasonPhrase}\n");
            }
        }

    }
}
