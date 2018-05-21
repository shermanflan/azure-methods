using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using System.Security.Cryptography.X509Certificates;

using Microsoft.IdentityModel.Clients.ActiveDirectory;

namespace UltiSecLib.Azure.OAuth2
{
    /*
     * Authenticates to Azure via a client certificate. Based on:
     * 
     *  1. https://github.com/Azure-Samples/active-directory-dotnet-daemon-certificate-credential
     * 
     * PS Steps to create cert:
     * # Create certificate.
     * $cert=New-SelfSignedCertificate -Subject "CN=TodoListDaemonWithCert" -CertStoreLocation "Cert:\CurrentUser\My"  -KeyExportPolicy Exportable -KeySpec Signature
     * 
     * # Create JSON manifest representation.
     * $bin = $cert.RawData
     * $base64Value = [System.Convert]::ToBase64String($bin)
     * $bin = $cert.GetCertHash()
     * $base64Thumbprint = [System.Convert]::ToBase64String($bin)
     * $keyid = [System.Guid]::NewGuid().ToString()
     * $jsonObj = @{customKeyIdentifier=$base64Thumbprint;keyId=$keyid;type="AsymmetricX509Cert";usage="Verify";value=$base64Value}
     * $keyCredentials=ConvertTo-Json @($jsonObj) | Out-File "C:\Users\ricardogu\Desktop\Personal\MyCerts\keyCredentials.txt"
     * 
     * Update Application manifest with JSON representation under "keyCredentials".
     * 
     * TODO:
     * - Add logging.
     */
    public class AuthByCertificate : IAuthorize
    {
        private static AuthenticationContext authContext = null;
        private static ClientAssertionCertificate certCred = null;

        public AuthByCertificate(string authority, string tenant, string client, string certName
                                , string resource)
        {
            Authority = authority;
            Tenant = tenant;
            ClientId = client;
            CertName = certName;
            APIResourceId = resource;

            InitializeContext();
        }

        private string Authority { get; set; }
        private string Tenant { get; set; }
        private string ClientId { get; set; }
        private string CertName { get; set; }
        private string APIResourceId { get; set; } // target API

        // Get an access token from Azure AD using client credentials.
        // If the attempt to get a token fails because the server is unavailable, 
        // retry twice after 3 seconds each.
        public async Task<AuthenticationResult> AcquireToken()
        {
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
                    if (ex.ErrorCode == "temporarily_unavailable" // server too busy
                        || ex.ErrorCode == AdalError.NetworkNotAvailable
                        || ex.ErrorCode == AdalError.ServiceUnavailable)
                    {
                        retry = true;
                        retryCount++;
                        Thread.Sleep(3000);
                    }

                    Debug.WriteLine($"An error occurred while acquiring a token\nTime: {DateTime.Now}\nError: {ex}\nRetry: {retry}\n");

                    throw;
                }

            } while ((retry == true) && (retryCount < 3));
            return result;
        }
        public void SignOut()
        {
            // Clear the token cache
            authContext.TokenCache.Clear();
        }

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

        private X509Certificate2 ReadCertificateFromStore()
        {
            X509Certificate2 cert = null;
            using (X509Store store = new X509Store(StoreName.My, StoreLocation.CurrentUser))
            {
                store.Open(OpenFlags.ReadOnly);
                X509Certificate2Collection certCollection = store.Certificates;

                // Find unexpired certificates.
                X509Certificate2Collection currentCerts = certCollection.Find(X509FindType.FindByTimeValid, DateTime.Now, false);

                // From the collection of unexpired certificates, find the ones with the correct name.
                X509Certificate2Collection signingCert = currentCerts.Find(X509FindType.FindBySubjectDistinguishedName, CertName, false);

                // Return the first certificate in the collection, has the right name and is current.
                cert = signingCert.OfType<X509Certificate2>().OrderByDescending(c => c.NotBefore).FirstOrDefault();

                //store.Close();
            }

            return cert;
        }
    }
}
