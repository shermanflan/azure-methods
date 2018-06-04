using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Net.Http;
using System.Net.Http.Headers;
using Microsoft.IdentityModel.Clients.ActiveDirectory;
using System.Globalization;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

using UltiSecLib.Azure.OAuth2;

namespace AzureOAuthClient.D365.Dmf
{
    public class D365DmfAPI
    {
        private IAuthorize authKey = null;

        private string Authority { get; set; }
        private string Tenant { get; set; }
        private string ClientId { get; set; }
        private string AppKey { get; set; }
        private string APIResourceId { get; set; } // target API
        private string APIEndpoint { get; set; }

        public D365DmfAPI(string authority, string tenant, string client, string appKey
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

        private void InitializeContext()
        {
            authKey = new AuthByAppKey(Authority, Tenant, ClientId, AppKey, APIResourceId);
        }

        // Invoke DMF API
        public async Task<string> GetBlobURI(string name)
        {
            // Get an Access Token for the API
            AuthenticationResult result = await authKey.AcquireToken();
            string blobId = "";
            string blobURI = "";

            // Once we have an access_token, invoke API.
            using (HttpClient httpClient = new HttpClient())
            {
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

                string d365Request = String.Format(CultureInfo.InvariantCulture
                                                    , "{0}/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.GetAzureWriteUrl"
                                                    , APIEndpoint);

                string jsonBody = JsonConvert.SerializeObject(new { uniqueFileName = name });

                HttpResponseMessage response = await httpClient.PostAsync(d365Request, new StringContent(jsonBody, Encoding.UTF8, "application/json"));

                if (response.IsSuccessStatusCode)
                {
                    // Read the response and output it to the console.
                    string content = await response.Content.ReadAsStringAsync();

                    try
                    {
                        // TODO: Use canonical JSON deserialization methods.
                        JObject inputJson = JsonConvert.DeserializeObject<JObject>(content);
                        JValue objJson = inputJson["value"] as JValue;

                        // Parse string value as JSON
                        // TODO: Do I need to set a json response/accept header?
                        blobId = JsonConvert.DeserializeObject<JObject>(inputJson["value"].ToString())["BlobId"].ToString();
                        blobURI = JsonConvert.DeserializeObject<JObject>(inputJson["value"].ToString())["BlobUrl"].ToString();

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

            return String.Format("ID: {0}, URL: {1}", blobId, blobURI);
        }

        // TODO
        public async Task UploadBlobToURI(string id, string uri)
        {
            throw new NotImplementedException("TODO");
        }
    }
}
