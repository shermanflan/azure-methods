using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using System.Configuration;
using RestSharp;
using UtilitiesPOC;

namespace ConsoleAppTester.RESTUtility
{
    /************************************************************************************
     * 3rd party REST methods.
     ************************************************************************************/
    public class ThirdParty
    {
        private static readonly string cnxn = ConfigurationManager.AppSettings["funappdemo"];
        private static readonly string code = ConfigurationManager.AppSettings["code"];

        public string Ex1_RestSharpGET()
        {
            string baseURI = "https://funappdemo01.azurewebsites.net/api/VSRequestSecure";
            string paramsURI = $"?code={code}&name=Ricardo%20Guzman";

            var uri01 = new Uri(baseURI + '/' + paramsURI);
            var client = new RestClient(uri01);

            IRestResponse<TypedQueueMessage> response = client.ExecuteAsGet<TypedQueueMessage>(new RestRequest(), httpMethod: "GET");

            TypedQueueMessage m1 = response.Data;

            return m1.ToString();
        }

        public async Task<string> Ex1_RestSharpGETAsync()
        {
            string baseURI = "https://funappdemo01.azurewebsites.net/api/VSRequestSecure";
            string paramsURI = $"?code={code}&name=Ricardo%20Guzman";

            var uri01 = new Uri(baseURI + '/' + paramsURI);
            var client = new RestClient(uri01);

            var response = await client.ExecuteTaskAsync<TypedQueueMessage>(new RestRequest());

            TypedQueueMessage m1 = response.Data;

            return m1.ToString();
        }
    }
}
