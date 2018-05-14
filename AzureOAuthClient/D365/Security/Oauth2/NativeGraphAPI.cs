using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Globalization;

using Microsoft.IdentityModel.Clients.ActiveDirectory;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using Newtonsoft.Json.Linq;

namespace AzureOAuthClient.D365.Security.Oauth2
{
    /*
     * Example of accessing an Azure OAuth2 protected API from a native application. 
     * 
     * Steps:
     * 
     * 1. Install ADAL: Install-Package Microsoft.IdentityModel.Clients.ActiveDirectory
     * 2. Setup Application in Azure:
     *      a. Type: Native
     *      b. Redirct Uri: Can be any valid URI but use something descriptive
     *      c. Required Permissions > Microsoft Graph > Delegated > Read Directory Data
     * 3. Add tenant id, client id, resource id, etc as configurable parameters.
     * 
     * This is an example of an acquire token using the Select Account option. In this case,
     * the user will be prompted to choose an Azure account each time.
     * 
     */
    public class NativeGraphAPI
    {
        private static AuthenticationContext authContext = null;
        public string Authority { get; set; }
        public string Tenant { get; set; }
        public string ClientId { get; set; }
        public string RedirectUri { get; set; }
        public string GraphResourceId { get; set; } // target API
        public string GraphApiVersion { get; set; }
        public string GraphApiEndpoint { get; set; }

        public NativeGraphAPI(string authority, string tenant, string client, string redirect, string resource
                                , string apiVersion, string apiEndpoint)
        {
            Authority = authority;
            Tenant = tenant;
            ClientId = client;
            RedirectUri = redirect;
            GraphResourceId = resource;
            GraphApiVersion = apiVersion;
            GraphApiEndpoint = apiEndpoint;
            InitializeContext(Authority);
        }

        // TODO: Refactor to Oauth2 class.
        private void InitializeContext(string authority)
        {
            // Pass ADAL the coordinates it needs to communicate with Azure AD and tell it how to cache tokens.
            authContext = new AuthenticationContext(authority);
        }

        // TODO: Refactor to Oauth2 class.
        public async Task<AuthenticationResult> AcquireToken(string resource, string client, string redirectURL)
        {
            AuthenticationResult result = null;
            try
            {
                // 
                result = await authContext.AcquireTokenAsync(
                                                resource,
                                                client,
                                                new Uri(redirectURL),
                                                new PlatformParameters(PromptBehavior.SelectAccount) // Always | Auto | Never
                                            );
            }
            catch (AdalException ex)
            {
                Console.WriteLine($"AcquireToken: {ex.Message}");
            }

            return result;
        }

        // Invoke API
        public string GetUser(string prefix)
        {
            // Get an Access Token for the Graph API
            AuthenticationResult result = AcquireToken(GraphResourceId, ClientId, RedirectUri).Result;

            // Once we have an access_token, invoke API.
            //string searchText = "rrguzman1976";
            string graphRequest = String.Format(CultureInfo.InvariantCulture
                                    , "{0}{1}/users?$filter=startswith(userPrincipalName, '{2}')"
                                    , GraphApiEndpoint, Tenant, prefix);
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

            string user = jResult["value"].ToString();
            return user;
        }

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
    }
}
