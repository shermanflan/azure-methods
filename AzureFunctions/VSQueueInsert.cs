using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Host;

using UtilitiesPOC;

namespace AzureFunctions
{
    // Single message example.
    public static class VSQueueInsert
    {
        [FunctionName("VSQueueInsert")]
        public static HttpResponseMessage Run(
            [HttpTrigger(AuthorizationLevel.Anonymous, "get", "put", "post", Route = null)]HttpRequestMessage req
            , TraceWriter log
            , [Queue("outqueuerko03")] out TypedQueueMessage outputQueueMessage)
        {
            log.Info("C# HTTP trigger function processed a request.");

            // parse query parameter
            string message = req.GetQueryNameValuePairs()
                .FirstOrDefault(q => string.Compare(q.Key, "message", true) == 0)
                .Value;

            TypedQueueMessage msg = new TypedQueueMessage();

            if (message == null)
            {
                // Get request body
                dynamic data = req.Content.ReadAsAsync<object>().Result;

                msg.fname = data?.fname;
                msg.lname = data?.lname;
                msg.email = data?.email;
                msg.devicelist = data?.devicelist;

                message = data.ToString();
            }

            outputQueueMessage = msg;

            return message == null
                ? req.CreateResponse(HttpStatusCode.BadRequest, "Please pass a message on the query string or in the request body")
                : req.CreateResponse(HttpStatusCode.OK, "Hello " + message);
        }
    }
}
