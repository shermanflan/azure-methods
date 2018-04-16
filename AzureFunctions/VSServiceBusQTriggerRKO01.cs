using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.ServiceBus.Messaging;

namespace AzureFunctions
{
    public static class VSServiceBusQTriggerRKO01
    {
        [FunctionName("VSServiceBusQTriggerRKO01")]
        public static void Run([ServiceBusTrigger("rkoqueue01", AccessRights.Listen, Connection = "FunAppBusRKO01_RKOApp01_SERVICEBUS")]string myQueueItem, TraceWriter log)
        {
            log.Info($"C# ServiceBus queue trigger from VS function processed message: {myQueueItem}");
        }
    }
}
