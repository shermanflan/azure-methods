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
     * TODO:
     * 
     * 1. See NativeClient-DotNet for a token cache implementation.
     *      a. https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-devquickstarts-dotnet
     * 2. See here for acquire token silently pattern:
     *      a. https://github.com/AzureAD/azure-activedirectory-library-for-dotnet/wiki/AcquireTokenSilentAsync-using-a-cached-token
     * 2. Does the Auto option get silently called when the user is in an SSO context?
     */
    public class NativeAutoGraphAPI
    {
        private static AuthenticationContext authContext = null;
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

        // TODO: Refactor to Oauth2 class.
        private void InitializeContext(string authority)
        {
            // Pass ADAL the coordinates it needs to communicate with Azure AD and tell it how to cache tokens.
            authContext = new AuthenticationContext(authority);
        }

        // TODO: Refactor to Oauth2 class.
        public async Task<AuthenticationResult> AcquireToken(string resource, string client, string redirectURL)
        {
            // As the application starts, try to get an access token from cache without prompting the user.
            AuthenticationResult result = null;
            try
            {
                result = await authContext.AcquireTokenSilentAsync(
                                                resource, 
                                                client, 
                                                // Hint to use a specific account
                                                new UserIdentifier("rrguzman1976@hotmail.com", UserIdentifierType.OptionalDisplayableId)
                                            );

                Debug.WriteLine("Acquired token silenty.");
                return result;
            }
            catch (AdalException ex)
            {
                if (ex.ErrorCode != AdalError.FailedToAcquireTokenSilently
                    && ex.ErrorCode != AdalError.InteractionRequired)
                {
                    throw ex;
                }
            }

            // If one does not exist, prompt for access.
            try
            {
                // PromptBehavior.Auto will attempt to return a token without asking the user for credentials.
                // PromptBehavior.Never will tell ADAL that the user should not be prompted for sign in, 
                // and ADAL should instead throw an exception if it is unable to return a token.
                // TODO: Under SSO (ricardo_guzman@ulti), does the challenge prompt still popup with hint?
                result = await authContext.AcquireTokenAsync(
                                                resource,
                                                client,
                                                new Uri(redirectURL),
                                                new PlatformParameters(PromptBehavior.Auto), // Auto | Always | SelectAccount | Never
                                                                                             // Hint to use a specific account
                                                new UserIdentifier("rrguzman1976@hotmail.com", UserIdentifierType.OptionalDisplayableId)
                                                //new UserIdentifier("ricardo_guzman@ultimatesoftware.com", UserIdentifierType.OptionalDisplayableId)
                                            );

                Debug.WriteLine("Acquired token auto.");
            }
            catch (AdalException ex) // unable to return a token
            {
                Debug.WriteLine($"AcquireToken: {ex.Message}");
                throw ex;
            }

            return result;
        }

        public void SignOut()
        {
            // Clear the token cache
            authContext.TokenCache.Clear();
        }

        // Invoke API
        public string GetUser(string prefix)
        {
            // Get an Access Token for the Graph API
            AuthenticationResult result = AcquireToken(GraphResourceId, ClientId, RedirectUri).Result;

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
