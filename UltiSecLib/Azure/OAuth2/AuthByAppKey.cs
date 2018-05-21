using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.IdentityModel.Clients.ActiveDirectory;

namespace UltiSecLib.Azure.OAuth2
{
    /*
     * Implements Azure OAuth2 authorization by an Application Key. Based on:
     * 
     *  1. https://github.com/Azure-Samples/active-directory-dotnet-daemon
     */
    public class AuthByAppKey : IAuthorize
    {
        private static AuthenticationContext authContext = null;
        private static ClientCredential clientCredential = null;

        public AuthByAppKey(string authority, string tenant, string client, string appKey
                            , string resource)
        {
            Authority = authority;
            Tenant = tenant;
            ClientId = client;
            AppKey = appKey;
            APIResourceId = resource;

            InitializeContext();
        }

        public async Task<AuthenticationResult> AcquireToken()
        {
            // Get an access token from Azure AD using client credentials.
            AuthenticationResult result = null;
            int retryCount = 0;
            bool retry = false;

            do
            {
                retry = false;

                try
                {
                    // ADAL includes an in memory cache, so this call will only send a message 
                    // to the server if the cached token is expired.
                    result = await authContext.AcquireTokenAsync(APIResourceId, clientCredential);
                }
                catch (AdalException ex)
                {
                    if (ex.ErrorCode == "temporarily_unavailable" // server too busy
                        || ex.ErrorCode == AdalError.NetworkNotAvailable
                        || ex.ErrorCode == AdalError.ServiceUnavailable)
                    {
                        retry = true;
                        retryCount++;
                        Thread.Sleep(3000);
                    }

                    throw ex;
                }

            } while ((retry == true) && (retryCount < 3));

            return result;
        }

        private void InitializeContext()
        {
            // Pass ADAL the coordinates it needs to communicate with Azure AD and tell it how to cache tokens.
            authContext = new AuthenticationContext(Authority);

            clientCredential = new ClientCredential(ClientId, AppKey);
        }

        private string Authority { get; set; }
        private string Tenant { get; set; }
        private string ClientId { get; set; }
        private string AppKey { get; set; }
        private string APIResourceId { get; set; } // target API

    }
}
