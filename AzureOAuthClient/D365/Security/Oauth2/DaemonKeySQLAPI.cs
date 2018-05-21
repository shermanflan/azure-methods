using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using Microsoft.IdentityModel.Clients.ActiveDirectory;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Globalization;
using Newtonsoft.Json;

using UltiSecLib.Azure.OAuth2;

namespace AzureOAuthClient.D365.Security.Oauth2
{
    /*
     * Uses the Windows Azure Service Management API to query the Azure SQL service.
     * Requires the application to be assigned the "Contributor" role at the Resource
     * Group level under the appropriate Subscription.
     * 
     * See here for details:
     * https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal
     */
    public class DaemonKeySQLAPI
    {
        private IAuthorize authKey = null;

        private string Authority { get; set; }
        private string Tenant { get; set; }
        private string ClientId { get; set; }
        private string AppKey { get; set; }
        private string APIResourceId { get; set; } // target API
        private string APIVersion { get; set; }
        private string APIEndpoint { get; set; }

        public DaemonKeySQLAPI(string authority, string tenant, string client, string appKey
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
        public async Task<string> GetDatabases()
        {
            // Get an Access Token for the AD Graph API
            AuthenticationResult result = await authKey.AcquireToken();

            // Once we have an access_token, invoke API.
            HttpClient httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);
            //httpClient.DefaultRequestHeaders.Add("api-version", APIVersion);

            // {0}subscriptions/bfc537d4-b3d2-4e7b-a636-f789f97f62da/resourceGroups/RKOSQLDB01/providers/Microsoft.Sql/servers/rkosqlsrv01/databases
            string graphRequest = String.Format(CultureInfo.InvariantCulture
                                                , "{0}subscriptions/bfc537d4-b3d2-4e7b-a636-f789f97f62da/resourceGroups/RKOSQLDB01/providers/Microsoft.Sql/servers/rkosqlsrv01/databases?api-version={1}"
                                                , APIEndpoint, APIVersion);

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
                    StringBuilder list = new StringBuilder();

                    foreach (var db in sequence)
                    {
                        list.AppendLine(db["name"].ToString());
                    }

                    return list.ToString();

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
