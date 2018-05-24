using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Globalization;

using Microsoft.IdentityModel.Clients.ActiveDirectory;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using Newtonsoft.Json.Linq;

using UltiSecLib.Azure.OAuth2;

namespace AzureOAuthClient.D365.Security.Oauth2
{
    public class DaemonAutoD365API
    {
        IAuthorize authConsent = null;

        public string Authority { get; set; }
        public string Tenant { get; set; }
        public string ClientId { get; set; }
        public string RedirectUri { get; set; }
        public string ApiResourceId { get; set; } // target API
        public string ApiEndpoint { get; set; }

        public DaemonAutoD365API(string authority, string tenant, string client, string redirect, string resource
                                , string apiEndpoint)
        {
            Debug.Listeners.Add(new TextWriterTraceListener(Console.Out));
            Debug.AutoFlush = true;

            Authority = authority;
            Tenant = tenant;
            ClientId = client;
            RedirectUri = redirect;
            ApiResourceId = resource;
            ApiEndpoint = apiEndpoint;
            InitializeContext(Authority);
        }

        private void InitializeContext(string authority)
        {
            authConsent = new AuthByConsent(Authority, Tenant, ClientId, RedirectUri, ApiResourceId);
        }

        // Invoke API
        public string GetCustomer(string name)
        {
            // Get an Access Token for the Graph API
            AuthenticationResult result = authConsent.AcquireToken().Result;

            // Once we have an access_token, invoke API.
            string d365Request = String.Format(CultureInfo.InvariantCulture
                                    , "{0}/data/Customers?$filter=Name eq '{1}'", ApiEndpoint, name);
            HttpRequestMessage request = new HttpRequestMessage(HttpMethod.Get, d365Request);

            // Oauth2 Access Token
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", result.AccessToken);

            using (HttpClient httpClient = new HttpClient())
            {
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
        }
    }
}
