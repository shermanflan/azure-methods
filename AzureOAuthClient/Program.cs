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

        private static string clientid = ConfigurationManager.AppSettings["app1:ClientId"];
        private static string redirectUri = ConfigurationManager.AppSettings["app1:RedirectUri"];
        private static string graphResourceId = ConfigurationManager.AppSettings["app1:GraphResourceId"]; // target API
        private static string graphApiVersion = ConfigurationManager.AppSettings["app1:GraphApiVersion"];
        private static string graphApiEndpoint = ConfigurationManager.AppSettings["app1:GraphEndpoint"];

        private static string clientid2 = ConfigurationManager.AppSettings["app2:ClientId"];
        private static string appKey = ConfigurationManager.AppSettings["app2:AppKey"];
        private static string APIResourceId2 = ConfigurationManager.AppSettings["app2:APIResourceId"]; // target API
        private static string APIVersion2 = ConfigurationManager.AppSettings["app2:ApiVersion"];
        private static string APIEndpoint2 = ConfigurationManager.AppSettings["app2:APIBaseAddress"];

        private static string clientid3 = ConfigurationManager.AppSettings["app3:ClientId"];
        private static string certName = ConfigurationManager.AppSettings["app3:CertName"];
        private static string App3APIResourceId = ConfigurationManager.AppSettings["app3:APIResourceId"]; // target API
        private static string App3APIVersion = ConfigurationManager.AppSettings["app3:APIVersion"]; // target API
        private static string App3ApiEndpoint = ConfigurationManager.AppSettings["app3:APIBaseAddress"];

        private static string clientid4 = ConfigurationManager.AppSettings["app4:ClientId"];
        private static string appKey4 = ConfigurationManager.AppSettings["app4:AppKey"];
        private static string APIResourceId4 = ConfigurationManager.AppSettings["app4:APIResourceId"]; // target API
        private static string APIVersion4 = ConfigurationManager.AppSettings["app4:ApiVersion"];
        private static string APIEndpoint4 = ConfigurationManager.AppSettings["app4:APIBaseAddress"];

        public static void Main(string[] args)
        {
            string authority = String.Format(CultureInfo.InvariantCulture, aadInstance, tenant);

            try
            {
                //NativeAutoGraphAPI api = new NativeAutoGraphAPI(authority, tenant, clientid, redirectUri, graphResourceId, graphApiVersion, graphApiEndpoint);
                //api.SignOut();
                //Console.WriteLine($"GetUser: {api.GetUser("rrguzman1976")}");
                //Console.WriteLine($"WhoAmI: {api.WhoAmI()}");

                //DaemonKeyGraphAPI api2 = new DaemonKeyGraphAPI(authority, tenant, clientid2, appKey, APIResourceId2, APIVersion2, APIEndpoint2);
                //Console.WriteLine($"GetUser: {api2.GetUser("Ricardo").Result}");

                //DaemonCertGraphAPI api3 = new DaemonCertGraphAPI(authority, tenant, clientid3, certName, App3APIResourceId, App3APIVersion, App3ApiEndpoint);
                //Console.WriteLine($"GetUser: {api3.GetUser("Ric").Result}");

                //DaemonKeySQLAPI api4 = new DaemonKeySQLAPI(authority, tenant, clientid4, appKey4, APIResourceId4, APIVersion4, APIEndpoint4);
                //Console.WriteLine($"Get Databases:\n{api4.GetDatabases().Result}");

            }
            catch (Exception e)
            {
                Console.WriteLine($"{e.ToString()}");
            }

            Console.ReadLine();
        }
    }
}
