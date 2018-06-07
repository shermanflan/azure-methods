using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using System.Configuration;
using System.Globalization;

using AzureOAuthClient.D365.Security.Oauth2;
using AzureOAuthClient.D365.Dmf;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace AzureOAuthClient
{
    public class Program
    {
        private static string aadInstance = ConfigurationManager.AppSettings["AADInstance"];
        private static string tenant = ConfigurationManager.AppSettings["Tenant"];
        private static string tenant2 = ConfigurationManager.AppSettings["Tenant2"];

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
        private static string App3APIVersion = ConfigurationManager.AppSettings["app3:APIVersion"];
        private static string App3ApiEndpoint = ConfigurationManager.AppSettings["app3:APIBaseAddress"];

        private static string clientid4 = ConfigurationManager.AppSettings["app4:ClientId"];
        private static string appKey4 = ConfigurationManager.AppSettings["app4:AppKey"];
        private static string APIResourceId4 = ConfigurationManager.AppSettings["app4:APIResourceId"]; // target API
        private static string APIVersion4 = ConfigurationManager.AppSettings["app4:ApiVersion"];
        private static string APIEndpoint4 = ConfigurationManager.AppSettings["app4:APIBaseAddress"];

        private static string clientid5 = ConfigurationManager.AppSettings["app5:ClientId"];
        private static string appKey5 = ConfigurationManager.AppSettings["app5:AppKey"];
        private static string redirectUri5 = ConfigurationManager.AppSettings["app5:RedirectUri"];
        private static string APIResourceId5 = ConfigurationManager.AppSettings["app5:APIResourceId"]; // target API
        private static string APIEndpoint5 = ConfigurationManager.AppSettings["app5:APIBaseAddress"];

        private static string clientid6 = ConfigurationManager.AppSettings["app6:ClientId"];
        private static string redirectUri6 = ConfigurationManager.AppSettings["app6:RedirectUri"];
        private static string APIResourceId6 = ConfigurationManager.AppSettings["app6:APIResourceId"]; // target API
        private static string APIEndpoint6 = ConfigurationManager.AppSettings["app6:APIBaseAddress"];

        public static void Main(string[] args)
        {
            string authority = String.Format(CultureInfo.InvariantCulture, aadInstance, tenant);
            string authority2 = String.Format(CultureInfo.InvariantCulture, aadInstance, tenant2);

            try
            {
                //NativeAutoGraphAPI api = new NativeAutoGraphAPI(authority, tenant, clientid, redirectUri, graphResourceId, graphApiVersion, graphApiEndpoint);
                //api.SignOut();
                //Console.WriteLine($"GetUser: {api.GetUser("rrguzman1976")}");
                //Console.WriteLine($"WhoAmI: {api.WhoAmI()}");

                //DaemonKeyGraphAPI api2 = new DaemonKeyGraphAPI(authority, tenant, clientid2, appKey, APIResourceId2, APIVersion2, APIEndpoint2);
                //Console.WriteLine($"GetUser: {DaemonKeyGraphAPI.GetUser("Ricardo").Result}");

                //DaemonCertGraphAPI api3 = new DaemonCertGraphAPI(authority, tenant, clientid3, certName, App3APIResourceId, App3APIVersion, App3ApiEndpoint);
                //Console.WriteLine($"GetUser: {api3.GetUser("Ric").Result}");

                //DaemonKeySQLAPI api4 = new DaemonKeySQLAPI(authority, tenant, clientid4, appKey4, APIResourceId4, APIVersion4, APIEndpoint4);
                //Console.WriteLine($"Get Databases:\n{api4.GetDatabases().Result}");

                //DaemonKeyD365API api5 = new DaemonKeyD365API(authority2, tenant2, clientid5, appKey5, APIResourceId5, APIEndpoint5);
                //Console.WriteLine($"Companies:\n{api5.GetAllCustomers().Result}");
                //Console.WriteLine($"Jobs:\n{api5.GetAllJobs().Result}");

                //DaemonAutoD365API api6 = new DaemonAutoD365API(authority2, tenant2, clientid6, redirectUri6, APIResourceId6, APIEndpoint6);
                //Console.WriteLine($"Get Company: {api6.GetCustomer("Contoso Europe")}");

                D365DmfAPI api7 = new D365DmfAPI(authority2, tenant2, clientid5, appKey5, APIResourceId5, APIEndpoint5);

                string fileGUID = Guid.NewGuid().ToString();

                Console.WriteLine($"Gen GUID: {fileGUID}");

                string writeURI = api7.GetBlobURI(fileGUID).Result;

                Console.WriteLine($"Blob: {writeURI}");

                string payload = @"C:\Users\ricardogu\Desktop\Personal\Data\RKOPositionTypes_Import.zip";

                api7.UploadBlobToURI(filePath: payload, uri: writeURI).Wait();

                string resource = String.Format(CultureInfo.InvariantCulture
                                                , "{0}/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.ImportFromPackageAsync"
                                                //, "{0}/data/DataManagementDefinitionGroups/Microsoft.Dynamics.DataEntities.ImportFromPackage"
                                                , APIResourceId5);

                string execId = api7.ImportFromPackage(
                    dmfProject: "RKOImportPositionTypes", blobUri: writeURI, dmfUri: resource, legalEntity: "USMF"
                ).Result;

                Console.WriteLine($"Execution Id!: {execId}");
            }
            catch (Exception e)
            {
                Console.WriteLine($"{e.ToString()}");
            }

            Console.ReadLine();
        }
    }
}
