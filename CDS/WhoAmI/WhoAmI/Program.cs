using Microsoft.IdentityModel.Clients.ActiveDirectory;
using Newtonsoft.Json.Linq;
using System;
using System.Configuration;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;

namespace WhoAmI
{
    public class Program
    {
        public static void Main(string[] args)
        {
            // Azure Active Directory registered app clientid for Microsoft samples
            string url = null; 
            string tenantId = null;
            string clientId = null;
            string clientSecret = null;

            try
            {
                var appSettings = ConfigurationManager.AppSettings;

                if (appSettings.Count == 0)
                {
                    Console.WriteLine("AppSettings is empty.");
                    return;
                }

                url = appSettings["AADResource"];
                tenantId = appSettings["AADTenant"];
                //clientId = appSettings["AADClientMulti"];
                //clientSecret = appSettings["AADSecretMulti"];
                clientId = appSettings["AADClient"];
                clientSecret = appSettings["AADSecret"];

            }
            catch (ConfigurationErrorsException)
            {
                Console.WriteLine("Error reading app settings");
            }

            string authority = $"https://login.microsoftonline.com/{tenantId}";
            string apiVersion = "9.1";  // also, 9.0
            string webApiUrl = $"{url}/api/data/v{apiVersion}/";

            // Authenticate using IdentityModel.Clients.ActiveDirectory
            var clientCredential = new ClientCredential(clientId, clientSecret);
            var authContext = new AuthenticationContext(authority, false);
            var authResult = authContext.AcquireTokenAsync(url, clientCredential).Result;
            var authHeader = new AuthenticationHeaderValue("Bearer", authResult.AccessToken);

            var app = new Program();

            using (var client = new HttpClient())
            {
                client.BaseAddress = new Uri(webApiUrl);
                client.DefaultRequestHeaders.Authorization = authHeader;
                client.DefaultRequestHeaders.Add("Accept", "application/json");
                client.DefaultRequestHeaders.Add("OData-MaxVersion", "4.0");
                client.DefaultRequestHeaders.Add("OData-Version", "4.0");

                // GET: the WhoAmI function
                app.GetWhoAmI(client);
                //Task t = app.GetWhoAmIAsync(client);
                //t.Wait();
            }
        }

        public void GetWhoAmI(HttpClient client)
        {
            // GET: the WhoAmI function
            var response = client.GetAsync("WhoAmI").Result;

            if (response.IsSuccessStatusCode)
            {
                //Get the response content and parse it.  
                JObject body = JObject.Parse(response.Content.ReadAsStringAsync().Result);
                Guid userId = (Guid)body["UserId"];
                Console.WriteLine("Your UserId is {0}", userId);
                Console.WriteLine("Your OrganizationId is {0}", body["OrganizationId"]);
            }
            else
            {
                Console.WriteLine("The request failed with a status of '{0}'", response.ReasonPhrase);
            }

            Console.WriteLine("Press any key to exit.");
            Console.ReadLine();
        }

        public async Task GetWhoAmIAsync(HttpClient client)
        {
            // GET: the WhoAmI function
            var response = await client.GetAsync("WhoAmI");

            if (response.IsSuccessStatusCode)
            {
                //Get the response content and parse it.
                var content = await response.Content.ReadAsStringAsync();
                JObject body = JObject.Parse(content);
                Guid userId = (Guid)body["UserId"];
                Console.WriteLine("Your UserId is {0}", userId);
                Console.WriteLine("Your OrganizationId is {0}", body["OrganizationId"]);
            }
            else
            {
                Console.WriteLine("The request failed with a status of '{0}'", response.ReasonPhrase);
            }

            Console.WriteLine("Press any key to exit.");
            Console.ReadLine();
        }
    }
}
