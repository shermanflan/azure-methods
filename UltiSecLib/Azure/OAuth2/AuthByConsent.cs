using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Microsoft.IdentityModel.Clients.ActiveDirectory;

namespace UltiSecLib.Azure.OAuth2
{
    public class AuthByConsent : IAuthorize
    {
        private static AuthenticationContext authContext = null;

        public AuthByConsent(string authority, string tenant, string client, string redirect, string resource)
        {
            Authority = authority;
            Tenant = tenant;
            ClientId = client;
            RedirectUri = redirect;
            APIResourceId = resource;

            InitializeContext(Authority);

        }

        public async Task<AuthenticationResult> AcquireToken()
        {
            // As the application starts, try to get an access token from cache without prompting the user.
            AuthenticationResult result = null;
            try
            {
                result = await authContext.AcquireTokenSilentAsync(
                                            APIResourceId,
                                            ClientId
                                            // Hint to use a specific account
                                            //, new UserIdentifier("rrguzman1976@hotmail.com", UserIdentifierType.OptionalDisplayableId)
                                            );

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
                result = await authContext.AcquireTokenAsync(
                                                APIResourceId,
                                                ClientId,
                                                new Uri(RedirectUri),
                                                new PlatformParameters(PromptBehavior.SelectAccount) // Auto | Always | SelectAccount | Never
                                                // Hint to use a specific account
                                                //, new UserIdentifier("rrguzman1976@hotmail.com", UserIdentifierType.OptionalDisplayableId)
                                            );

            }
            catch (AdalException ex) // unable to return a token
            {
                throw ex;
            }

            return result;
        }

        public void SignOut()
        {
            // Clear the token cache
            authContext.TokenCache.Clear();
        }

        private void InitializeContext(string authority)
        {
            // Pass ADAL the coordinates it needs to communicate with Azure AD and tell it how to cache tokens.
            authContext = new AuthenticationContext(authority);
        }

        private string Authority { get; set; }
        private string Tenant { get; set; }
        private string ClientId { get; set; }
        private string RedirectUri { get; set; }
        private string APIResourceId { get; set; } // target API
    }
}
