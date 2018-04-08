using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Azure.WebJobs.Host;

using UtilitiesPOC;
using Newtonsoft;
using Newtonsoft.Json;

namespace AzureFunctions
{
    public static class VSQueueInsertN
    {
        // Insert multiple messages
        /*
         * 
                {
	                "devices":
	                [
		                {
			                "type": "laptop",
			                "brand":"lenovo",
			                "model":"T440"
		                },
		                {
			                "type": "mobile",
			                "brand":"Mi",
			                "model":"Red Mi 4"
		                }
	                ]
                }
         */
        [FunctionName("VSQueueInsertN")]
        public static HttpResponseMessage Run(
            [HttpTrigger(AuthorizationLevel.Anonymous, "put", Route = null)]HttpRequestMessage req
            , TraceWriter log
            , [Queue("outqueuerko03")] IAsyncCollector<string> outputQueueMessage)
        {
            log.Info("C# HTTP trigger function processed a request.");

            var data = req.Content.ReadAsStringAsync().Result;
            dynamic inputJson = JsonConvert.DeserializeObject<dynamic>(data);

            for (int nIndex = 0; nIndex < inputJson.devices.Count; nIndex++)
            {
                outputQueueMessage.AddAsync(inputJson.devices[nIndex].ToString());
            }

            return req.CreateResponse(HttpStatusCode.OK, "Hello world");
        }
    }
}
