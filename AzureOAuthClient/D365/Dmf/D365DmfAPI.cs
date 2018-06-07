using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
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
                                                    , APIResourceId);

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

        public async Task UploadBlobToURI(string filePath, string uri)
        {
            // Upload the file to Dynamics 365 for Operations
            using (FileStream stream = new FileStream(filePath, FileMode.Open))
            {
                var blob = new CloudBlockBlob(new Uri(uri));
                await blob.UploadFromStreamAsync(stream);
            }
        }

        public async Task DownloadBlobFromURI(string filePath, string uri)
        {
            var blob = new CloudBlockBlob(new Uri(uri));
            await blob.DownloadToFileAsync(filePath, System.IO.FileMode.Create);
        }

        public async Task<string> ImportFromPackage(string dmfProject, string blobUri, string legalEntity)
        {
            // Get an Access Token for the API
            AuthenticationResult result = await authKey.AcquireToken();

            using (HttpClient httpClient = new HttpClient())
            {
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

                string dmfUri = String.Format(CultureInfo.InvariantCulture
                                                , "{0}/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.ImportFromPackageAsync"
                                                , APIResourceId);

                DynamicsPackageImport dp = new DynamicsPackageImport()
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

                // TODO: Use CancellationToken
                HttpResponseMessage response = await httpClient.PostAsync(dmfUri, new StringContent(jsonBody, UnicodeEncoding.UTF8, "application/json"));

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
        }

        public async Task<string> ExportToPackage(string dmfProject, string legalEntity)
        {
            // Get an Access Token for the API
            AuthenticationResult result = await authKey.AcquireToken();

            using (HttpClient httpClient = new HttpClient())
            {
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

                string dmfUri = String.Format(CultureInfo.InvariantCulture
                                                , "{0}/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.ExportToPackage"
                                                , APIResourceId);

                DynamicsPackageExport dp = new DynamicsPackageExport()
                {
                    definitionGroupId = dmfProject,
                    packageName = Guid.NewGuid().ToString(),
                    executionId = "",
                    reExecute = true,
                    legalEntityId = legalEntity
                };

                string jsonBody = JsonConvert.SerializeObject(dp);

                // TODO: Use CancellationToken
                HttpResponseMessage response = await httpClient.PostAsync(dmfUri, new StringContent(jsonBody, UnicodeEncoding.UTF8, "application/json"));

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
        }

        public async Task<string> GetExportedPackageURI(string execId)
        {
            // Get an Access Token for the API
            AuthenticationResult result = await authKey.AcquireToken();

            // Once we have an access_token, invoke API.
            using (HttpClient httpClient = new HttpClient())
            {
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

                string d365Request = String.Format(CultureInfo.InvariantCulture
                                                    , "{0}/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.GetExportedPackageUrl"
                                                    , APIResourceId);

                string jsonBody = JsonConvert.SerializeObject(new { executionId = execId });

                HttpResponseMessage response = await httpClient.PostAsync(d365Request, new StringContent(jsonBody, Encoding.UTF8, "application/json"));

                if (response.IsSuccessStatusCode)
                {
                    // Read the response and output it to the console.
                    string content = await response.Content.ReadAsStringAsync();

                    // TODO: Use canonical JSON deserialization methods.
                    JObject inputJson = JsonConvert.DeserializeObject<JObject>(content);

                    return inputJson["value"].ToString(); // URI
                }
                else
                {
                    throw new InvalidOperationException($"Failed to access API:  {response.ReasonPhrase}\n");
                }
            }
        }

        /*
         * Statuses:
         * Unknown
         * NotRun
         * Executing
         * Succeeded
         * PartiallySucceeded
         * Failed
         * Canceled
         */
        public async Task PollExecutionStatus(string execId, int sleep, int tries)
        {
            // Check for status
            string output;
            int maxLoop = tries;

            do
            {
                Console.WriteLine("Waiting for package to execution to complete");

                Thread.Sleep(sleep);
                maxLoop--;

                if (maxLoop <= 0)
                {
                    break;
                }

                Console.WriteLine("Checking status");

                output = await GetExecutionStatus(execId);

                Console.WriteLine($"Status of import: {output}");

            }
            while (output == "NotRun" || output == "Executing");
        }

        public async Task<string> GetExecutionStatus(string execId)
        {
            // Get an Access Token for the API
            AuthenticationResult result = await authKey.AcquireToken();

            using (var httpClient = new HttpClient())
            {
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

                string d365Request = String.Format(CultureInfo.InvariantCulture
                                                    , "{0}/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.GetExecutionSummaryStatus"
                                                    , APIResourceId, execId);

                string jsonBody = JsonConvert.SerializeObject(new { executionId = execId });

                HttpResponseMessage response = await httpClient.PostAsync(d365Request, new StringContent(jsonBody, UnicodeEncoding.UTF8, "application/json"));
                //HttpResponseMessage response = await httpClient.GetAsync(d365Request);  // blocks

                if (response.IsSuccessStatusCode)
                {
                    // Read the response and output it to the console.
                    string content = await response.Content.ReadAsStringAsync();

                    // TODO: Use canonical JSON deserialization methods.
                    JObject inputJson = JsonConvert.DeserializeObject<JObject>(content);

                    return inputJson["value"].ToString(); // execution status
                }
                else
                {
                    throw new InvalidOperationException($"Failed to access API:  {response.ReasonPhrase}\n");
                }
            }
        }
    }

    public class AzureUrlResult
    {
        public string BlobId { get; set; }

        public string BlobUrl { get; set; }
    }

    public struct DynamicsPackageImport
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

    public struct DynamicsPackageExport
    {
        public string definitionGroupId { get; set; }
        public string packageName { get; set; }
        public string executionId { get; set; }
        public bool reExecute { get; set; }
        public string legalEntityId { get; set; }
    }
}
