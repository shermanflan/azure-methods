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
using Microsoft.WindowsAzure.Storage.Blob;
using System.IO;

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
            AzureUrlResult urlResult = null;

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
                        urlResult = JsonConvert.DeserializeObject<AzureUrlResult>(inputJson["value"].ToString());

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

            return urlResult.BlobUrl;
        }

        // TODO: TEST
        public async Task UploadBlobToURI(string filePath, string uri)
        {
            // Upload the file to Dynamics 365 for Operations
            using (FileStream stream = new FileStream(filePath, FileMode.Open))
            {
                var blob = new CloudBlockBlob(new Uri(uri));
                await blob.UploadFromStreamAsync(stream);
            }
        }

        public async Task<string> ImportFromPackage(string dmfProject, string blobUri, string dmfUri, string legalEntity)
        {
            DynamicsPackage dp = new DynamicsPackage()
            {
                packageUrl = blobUri,
                definitionGroupId = "RKOImportPositionTypes",
                executionId = "",
                execute = true,
                overwrite = true,
                legalEntityId = legalEntity,
                failOnError = true,
                runAsyncWithoutBatch = true,
                thresholdToRunInBatch = 0
            };

            string jsonBody = JsonConvert.SerializeObject(dp);
            StringContent stringContent = new StringContent(jsonBody, UnicodeEncoding.UTF8, "application/json");

            // Get an Access Token for the API
            AuthenticationResult result = await authKey.AcquireToken();

            using (HttpClient httpClient = new HttpClient())
            {
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

                try
                {
                    // TODO: Use CancellationToken
                    HttpResponseMessage response = await httpClient.PostAsync(dmfUri, stringContent);

                    if (response.IsSuccessStatusCode)
                    {
                        // Read the response and output it to the console.
                        string content = await response.Content.ReadAsStringAsync();

                        // TODO: Use canonical JSON deserialization methods.
                        JObject inputJson = JsonConvert.DeserializeObject<JObject>(content);

                        return inputJson["value"].ToString(); // execution id
                    }
                    else
                    {
                        throw new InvalidOperationException($"Failed to access API:  {response.ReasonPhrase}\n");
                    }
                }
                catch (ArgumentNullException e)
                {
                    Console.WriteLine(e.ToString());
                }
                catch (HttpRequestException e)
                {
                    Console.WriteLine(e.ToString());
                }
            }

            return null;
        }
    }

    public class AzureUrlResult
    {
        public string BlobId { get; set; }

        public string BlobUrl { get; set; }
    }

    public struct DynamicsPackage
    {
        public string packageUrl { get; set; }
        public string definitionGroupId { get; set; }
        public string executionId { get; set; }
        public bool execute { get; set; }
        public bool overwrite { get; set; }
        public string legalEntityId { get; set; }

        public bool failOnError { get; set; } // async parameter only

        public bool runAsyncWithoutBatch { get; set; } // async parameter only

        public int thresholdToRunInBatch { get; set; } // async parameter only
    }
}
