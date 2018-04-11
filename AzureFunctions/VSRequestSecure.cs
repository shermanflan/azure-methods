using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Host;

using Newtonsoft.Json;
using UtilitiesPOC;

namespace AzureFunctions
{
    public static class VSRequestSecure
    {
        [FunctionName("VSRequestSecure")]
        public static async Task<HttpResponseMessage> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)]HttpRequestMessage req
            , TraceWriter log)
        {
            log.Info("C# HTTP trigger function processed a request.");

            // parse query parameter
            string name = req.GetQueryNameValuePairs()
                .FirstOrDefault(q => string.Compare(q.Key, "name", true) == 0)
                .Value;

            if (name == null)
            {
                // Get request body
                dynamic data = await req.Content.ReadAsAsync<object>();
                name = data?.name;
            }

            TypedQueueMessage msg = new TypedQueueMessage
            {
                fname = name,
                lname = "guzman",
                email = "emailathotmail.com",
                devicelist = "test01"
            };

            if (name == null)
            {
                return req.CreateResponse(HttpStatusCode.BadRequest, "Please pass a name on the query string or in the request body");
            }
            else
            {
                // NOTE: This double serializes.
                /*
                string jsonMsg = JsonConvert.SerializeObject(msg);
                var header = new MediaTypeHeaderValue("application/json");
                HttpResponseMessage rmsg = req.CreateResponse(HttpStatusCode.OK, jsonMsg, header);
                return req.CreateResponse(HttpStatusCode.OK, jsonMsg, header);
                */

                // This auto-serializes as JSON.
                return req.CreateResponse(HttpStatusCode.OK, msg);
            }


        }
    }
}
