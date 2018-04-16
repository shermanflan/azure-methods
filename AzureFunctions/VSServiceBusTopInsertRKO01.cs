using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Host;

using System.Configuration;
using UtilitiesPOC;
using Microsoft.ServiceBus.Messaging;
using Newtonsoft.Json;

namespace AzureFunctions
{
    public static class VSServiceBusTopInsertRKO01
    {
        [FunctionName("VSServiceBusTopInsertRKO01")]
        public static async Task<HttpResponseMessage> Run([HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)]HttpRequestMessage req, TraceWriter log)
        {
            log.Info("C# HTTP trigger function processed a request.");

            // Get request body
            dynamic data = await req.Content.ReadAsAsync<TypedQueueMessage>();

            string cnxn = ConfigurationManager.AppSettings["FunAppBusRKO01_RKOApp01_SERVICEBUS"];

            TopicClient topicClient = TopicClient.CreateFromConnectionString(cnxn, "rkotopic01");

            var jsonM = JsonConvert.SerializeObject(data);
            var message = new BrokeredMessage(jsonM);

            await topicClient.SendAsync(message);

            return req.CreateResponse(HttpStatusCode.OK, $"From VS: Insert Service Bus Queue message - {data.ToString()}");
        }
    }
}
