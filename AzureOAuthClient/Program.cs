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
        private static string TodoListResourceId = ConfigurationManager.AppSettings["app2:TodoListResourceId"]; // target API
        private static string TodoListApiEndpoint = ConfigurationManager.AppSettings["app2:TodoListBaseAddress"];

        public static void Main(string[] args)
        {
            string authority = String.Format(CultureInfo.InvariantCulture, aadInstance, tenant);

            try
            {
                //NativeAutoGraphAPI api = new NativeAutoGraphAPI(authority, tenant, clientid, redirectUri, graphResourceId, graphApiVersion, graphApiEndpoint);
                //Console.WriteLine($"GetUser: {api.GetUser("rrguzman1976")}");
                //Console.WriteLine($"WhoAmI: {api.WhoAmI()}");
                //api.SignOut();

                DaemonKeyGraphAPI api2 = new DaemonKeyGraphAPI(authority, tenant, clientid2, appKey
                                                            , TodoListResourceId, TodoListApiEndpoint);

                api2.PostTodo();
                Console.WriteLine($"GetUser: {api2.GetUser("rrguzman1976")}");
                //Console.WriteLine($"WhoAmI: {api2.WhoAmI()}");

            }
            catch (Exception e)
            {
                Console.WriteLine($"{e.Message}");
            }
            Console.ReadLine();
        }
    }
}
