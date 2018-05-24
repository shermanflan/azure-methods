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

using UltiSecLib.Azure.OAuth2;

namespace AzureOAuthClient.D365.Security.Oauth2
{
    public class DaemonKeyD365API
    {
        private IAuthorize authKey = null;

        private string Authority { get; set; }
        private string Tenant { get; set; }
        private string ClientId { get; set; }
        private string AppKey { get; set; }
        private string APIResourceId { get; set; } // target API
        private string APIEndpoint { get; set; }

        public DaemonKeyD365API(string authority, string tenant, string client, string appKey
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

        // Invoke API
        public async Task<string> GetCustomer(string name)
        {
            // Get an Access Token for the API
            AuthenticationResult result = await authKey.AcquireToken();
            StringBuilder list = new StringBuilder();

            // Once we have an access_token, invoke API.
            using (HttpClient httpClient = new HttpClient())
            {
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

                string d365Request = String.Format(CultureInfo.InvariantCulture
                                                    , "{0}/data/Customers?$filter=Name eq '{1}'"
                                                    , APIEndpoint, name);

                HttpResponseMessage response = await httpClient.GetAsync(d365Request);

                if (response.IsSuccessStatusCode)
                {
                    // Read the response and output it to the console.
                    string content = await response.Content.ReadAsStringAsync();

                    try
                    {
                        // TODO: Use canonical JSON deserialization methods.
                        dynamic inputJson = JsonConvert.DeserializeObject(content);
                        var sequence = inputJson["value"];

                        foreach (var db in sequence)
                        {
                            list.AppendLine(db["Name"].ToString());
                        }

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

            return list.ToString();
        }

        public async Task<string> GetAllCustomers()
        {
            // Get an Access Token for the API
            AuthenticationResult result = await authKey.AcquireToken();
            StringBuilder list = new StringBuilder();

            // Once we have an access_token, invoke API.
            using (HttpClient httpClient = new HttpClient())
            {
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

                string d365Request = String.Format(CultureInfo.InvariantCulture, "{0}/data/Customers", APIEndpoint);

                HttpResponseMessage response = await httpClient.GetAsync(d365Request);

                if (response.IsSuccessStatusCode)
                {
                    // Read the response and output it to the console.
                    string content = await response.Content.ReadAsStringAsync();

                    try
                    {
                        // TODO: Use canonical JSON deserialization methods.
                        dynamic inputJson = JsonConvert.DeserializeObject(content);
                        var sequence = inputJson["value"];

                        foreach (var db in sequence)
                        {
                            list.AppendLine($"Account: {db["CustomerAccount"]}, Name: {db["Name"]}, Invoice City: {db["InvoiceAddressCity"]}");
                        }

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

            return list.ToString();
        }

        public async Task<string> GetAllJobs()
        {
            // Get an Access Token for the API
            AuthenticationResult result = await authKey.AcquireToken();
            StringBuilder list = new StringBuilder();

            // Once we have an access_token, invoke API.
            using (HttpClient httpClient = new HttpClient())
            {
                httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

                string d365Request = String.Format(CultureInfo.InvariantCulture, "{0}/data/Jobs", APIEndpoint);

                HttpResponseMessage response = await httpClient.GetAsync(d365Request);

                if (response.IsSuccessStatusCode)
                {
                    // Read the response and output it to the console.
                    string content = await response.Content.ReadAsStringAsync();

                    try
                    {
                        // TODO: Use canonical JSON deserialization methods.
                        dynamic inputJson = JsonConvert.DeserializeObject(content);
                        var sequence = inputJson["value"];

                        foreach (var db in sequence)
                        {
                            list.AppendLine($"JobId: {db["JobId"]}, Description: {db["Description"]}, JobDescription: {db["JobDescription"]}");
                        }

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

            return list.ToString();
        }

    }
}
