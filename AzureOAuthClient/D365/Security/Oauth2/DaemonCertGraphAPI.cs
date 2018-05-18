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
     * Successful API calls to AD Graph require the following minimum permissions:
     *  1. Microsoft Graph: Application/Read directory data
     *  2. Microsoft Graph: Delegated/Read directory data
     *  3. Windows Azure Active Directory: Application/Read directory data
     *  4. Windows Azure Active Directory: Delegated/Sign in and read user profile
     * Finally, explict permissions need to be granted (Settings > Required Permissions > Grant Permissions
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
                    if (ex.ErrorCode == "temporarily_unavailable"
                        || ex.ErrorCode == AdalError.NetworkNotAvailable
                        || ex.ErrorCode == AdalError.ServiceUnavailable)
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
        public async Task<string> GetUser(string prefix)
        {
            // Get an Access Token for the Graph API
            AuthenticationResult result = await AcquireToken();

            // Once we have an access_token, invoke API.
            HttpClient httpClient = new HttpClient();

            // Oauth2 Access Token
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
