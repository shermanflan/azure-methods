#define DEBUG

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
using System.Diagnostics;

using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UltiSecLib.Azure.OAuth2;

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
     * This is an example of an acquire token using the Auto option. In this case,
     * the user will be prompted to choose an Azure account iff a token does not
     * already exist. To delete an Azure "native" application, set the
     * "availableToOtherTenants" property to false in the manifest. Then delete.
     * 
     * Also uses Newtonsoft.Json.
     * 
     * NOTES:
     * 
     * 1. See NativeClient-DotNet for a token cache implementation.
     *      a. https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-devquickstarts-dotnet
     * 2. See here for acquire token silently pattern:
     *      a. https://github.com/AzureAD/azure-activedirectory-library-for-dotnet/wiki/AcquireTokenSilentAsync-using-a-cached-token
     */
    public class NativeAutoGraphAPI
    {
        IAuthorize authConsent = null;
        
        public string Authority { get; set; }
        public string Tenant { get; set; }
        public string ClientId { get; set; }
        public string RedirectUri { get; set; }
        public string GraphResourceId { get; set; } // target API
        public string GraphApiVersion { get; set; }
        public string GraphApiEndpoint { get; set; }

        public NativeAutoGraphAPI(string authority, string tenant, string client, string redirect, string resource
                                , string apiVersion, string apiEndpoint)
        {
            Debug.Listeners.Add(new TextWriterTraceListener(Console.Out));
            Debug.AutoFlush = true;

            Authority = authority;
            Tenant = tenant;
            ClientId = client;
            RedirectUri = redirect;
            GraphResourceId = resource;
            GraphApiVersion = apiVersion;
            GraphApiEndpoint = apiEndpoint;
            InitializeContext(Authority);
        }

        private void InitializeContext(string authority)
        {
            authConsent = new AuthByConsent(Authority, Tenant, ClientId, RedirectUri, GraphResourceId);
        }
        public void SignOut()
        {
            authConsent.SignOut();
        }

        // Invoke API
        public string GetUser(string prefix)
        {
            // Get an Access Token for the Graph API
            AuthenticationResult result = authConsent.AcquireToken().Result;

            // Once we have an access_token, invoke API.
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

            return jResult["value"].First["surname"] + ", " + jResult["value"].First["givenName"];
        }

        public string WhoAmI()
        {
            // Get an Access Token for the Graph API
            AuthenticationResult result = authConsent.AcquireToken().Result;

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
