using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using System.Configuration;
using System.Globalization;

using AzureOAuthClient.D365.Security.Oauth2;

namespace AzureOAuthClient
{
    public class Program
    {
        private static string aadInstance = ConfigurationManager.AppSettings["AADInstance"];
        private static string tenant = ConfigurationManager.AppSettings["Tenant"];
        private static string clientid = ConfigurationManager.AppSettings["ClientId"];
        private static string redirectUri = ConfigurationManager.AppSettings["RedirectUri"];
        private static string graphResourceId = ConfigurationManager.AppSettings["GraphResourceId"]; // target API
        private static string graphApiVersion = ConfigurationManager.AppSettings["GraphApiVersion"];
        private static string graphApiEndpoint = ConfigurationManager.AppSettings["GraphEndpoint"];

        public static void Main(string[] args)
        {
            string authority = String.Format(CultureInfo.InvariantCulture, aadInstance, tenant);
            NativeGraphAPI api = new NativeGraphAPI(authority, tenant, clientid, redirectUri, graphResourceId, graphApiVersion, graphApiEndpoint);

            // Show Search Results
            //Console.WriteLine($"GetUser: {api.GetUser("rrguzman1976")}");
            Console.WriteLine($"WhoAmI: {api.WhoAmI()}");

            Console.WriteLine($"");
            Console.ReadLine();
        }
    }
}
