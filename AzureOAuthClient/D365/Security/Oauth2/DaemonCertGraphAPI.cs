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
using System.Security.Cryptography.X509Certificates;

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
     *  1. https://github.com/Azure-Samples/active-directory-dotnet-daemon-certificate-credential
     * 
     * Cannot get this to work against a public API (Graph API). "Forbidden"
     * is returned. 
     */
    public class DaemonCertGraphAPI
    {
        private static AuthenticationContext authContext = null;
        private static ClientAssertionCertificate certCred = null;

        public string Authority { get; set; }
        public string Tenant { get; set; }
        public string ClientId { get; set; }
        public string CertName { get; set; }

        public string APIResourceId { get; set; } // target API
        public string APIVersion { get; set; }
        public string APIEndpoint { get; set; }

        public DaemonCertGraphAPI(string authority, string tenant, string client, string certName
                                , string resource, string version, string apiEndpoint)
        {
            Debug.Listeners.Add(new TextWriterTraceListener(Console.Out));
            Debug.AutoFlush = true;

            Authority = authority;
            Tenant = tenant;
            ClientId = client;
            CertName = certName;
            APIResourceId = resource;
            APIVersion = version;
            APIEndpoint = apiEndpoint;

            InitializeContext();
        }

        // TODO: Refactor to Oauth2 class.
        private void InitializeContext()
        {
            // Pass ADAL the coordinates it needs to communicate with Azure AD and tell it how to cache tokens.
            authContext = new AuthenticationContext(Authority);

            // Initialize the Certificate Credential to be used by ADAL.
            X509Certificate2 cert = ReadCertificateFromStore();
            if (cert == null)
            {
                throw new InvalidOperationException($"Cannot find active certificate '{CertName}' in certificates for current user. Please check configuration");
            }

            // Then create the certificate credential client assertion.
            certCred = new ClientAssertionCertificate(ClientId, cert);
        }

        /// <summary>
        /// Reads the certificate
        /// </summary>
        private X509Certificate2 ReadCertificateFromStore()
        {
            X509Certificate2 cert = null;
            X509Store store = new X509Store(StoreName.My, StoreLocation.CurrentUser);
            store.Open(OpenFlags.ReadOnly);
            X509Certificate2Collection certCollection = store.Certificates;

            // Find unexpired certificates.
            X509Certificate2Collection currentCerts = certCollection.Find(X509FindType.FindByTimeValid, DateTime.Now, false);

            // From the collection of unexpired certificates, find the ones with the correct name.
            X509Certificate2Collection signingCert = currentCerts.Find(X509FindType.FindBySubjectDistinguishedName, CertName, false);

            // Return the first certificate in the collection, has the right name and is current.
            cert = signingCert.OfType<X509Certificate2>().OrderByDescending(c => c.NotBefore).FirstOrDefault();
            store.Close();
            return cert;
        }

        // TODO: Refactor to Oauth2 class.
        public async Task<AuthenticationResult> AcquireToken()
        {
            //
            // Get an access token from Azure AD using client credentials.
            // If the attempt to get a token fails because the server is unavailable, retry twice after 3 seconds each.
            //
            AuthenticationResult result = null;
            int retryCount = 0;
            bool retry = false;

            do
            {
                retry = false;

                try
                {
                    // ADAL includes an in memory cache, so this call will only send a message to the server if the cached token is expired.
                    result = await authContext.AcquireTokenAsync(APIResourceId, certCred);
                }
                catch (AdalException ex)
                {
                    if (ex.ErrorCode == "temporarily_unavailable")
                    {
                        retry = true;
                        retryCount++;
                        Thread.Sleep(3000);
                    }

                    Console.WriteLine(
                        String.Format("An error occurred while acquiring a token\nTime: {0}\nError: {1}\nRetry: {2}\n",
                        DateTime.Now.ToString(),
                        ex.ToString(),
                        retry.ToString()));
                }

            } while ((retry == true) && (retryCount < 3));
            return result;
        }

        // Invoke API
        public async Task PostData()
        {
            // Get an access token from Azure AD using client credentials.
            // If the attempt to get a token fails because the server is unavailable, retry twice after 3 seconds each.
            AuthenticationResult result = await AcquireToken();

            // Post an item to the service.

            // Add the access token to the authorization header of the request.
            HttpClient httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

            // Forms encode data and POST to the web api.
            string timeNow = DateTime.Now.ToString();
            Console.WriteLine("Posting to To Do list at {0}", timeNow);
            string todoText = "RKO Task at time: " + timeNow;
            HttpContent content = new FormUrlEncodedContent(new[] { new KeyValuePair<string, string>("Title", todoText) });
            HttpResponseMessage response = await httpClient.PostAsync(APIEndpoint + "/api/todolist", content);

            if (response.IsSuccessStatusCode == true)
            {
                Console.WriteLine("Successfully posted new To Do item:  {0}\n", todoText);
            }
            else
            {
                Console.WriteLine("Failed to post a new To Do item\nError:  {0}\n", response.ReasonPhrase);
            }
        }

        public async Task<string> GetData()
        {
            // Get an Access Token for the API
            AuthenticationResult result = await AcquireToken();

            // Once we have an access_token, invoke API.
            HttpClient httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);
            HttpResponseMessage response = await httpClient.GetAsync(APIEndpoint + "/api/todolist");

            StringBuilder data = new StringBuilder();
            if (response.IsSuccessStatusCode)
            {
                // Read the response and output it to the console.
                var content = await response.Content.ReadAsStringAsync();

                try
                {
                    var inputJson = JsonConvert.DeserializeObject<List<TodoItem>>(content);

                    foreach (var t in inputJson)
                    {
                        data.AppendLine(t.ToString());
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

            return data.ToString();
        }

        // Invoke API
        // TODO: Returns "Forbidden"
        public async Task<string> GetUser(string prefix)
        {
            // Get an Access Token for the Graph API
            AuthenticationResult result = await AcquireToken();

            // Once we have an access_token, invoke API.
            string graphRequest = String.Format(CultureInfo.InvariantCulture
                                    , "{0}{1}/users?$filter=startswith(userPrincipalName, '{2}')"
                                    , APIEndpoint, Tenant, prefix);
            HttpRequestMessage request = new HttpRequestMessage(HttpMethod.Get, graphRequest);

            // Oauth2 Access Token
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

            HttpClient httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("api-version", APIVersion);
            HttpResponseMessage response = await httpClient.SendAsync(request);

            if (!response.IsSuccessStatusCode)
            {
                throw new WebException(response.StatusCode.ToString() + ": " + response.ReasonPhrase);
            }

            string content = await response.Content.ReadAsStringAsync();
            string val01 = null;

            try
            {
                var inputJson = JsonConvert.DeserializeObject<dynamic>(content);
            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
                throw;
            }

            return val01;
        }

    }
}
