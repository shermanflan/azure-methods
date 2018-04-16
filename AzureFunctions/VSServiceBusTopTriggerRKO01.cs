using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.ServiceBus.Messaging;

namespace AzureFunctions
{
    public static class VSServiceBusTopTriggerRKO01
    {
        [FunctionName("VSServiceBusTopTriggerRKO01")]
        public static void Run([ServiceBusTrigger("rkotopic01", "ConsoleAppTester", AccessRights.Listen, Connection = "FunAppBusRKO01_RKOApp01_SERVICEBUS")]string mySbMsg, TraceWriter log)
        {
            log.Info($"C# ServiceBus topic trigger from VS function processed message: {mySbMsg}");
        }
    }
}
