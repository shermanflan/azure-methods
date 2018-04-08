using System;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Host;

using UtilitiesPOC;

namespace AzureFunctions
{
    public static class VSQueueTriggerRKO01
    {
        [FunctionName("VSQueueTriggerRKO01")]
        public static void Run(
            [QueueTrigger("outqueuerko02", Connection = "AzureWebJobsStorage")]
            //string myQueueItem
            TypedQueueMessage myQueueItem
            , TraceWriter log)
        {
            log.Info($"C# Queue trigger function processed: {myQueueItem}");
            log.Info($"Typed access: {myQueueItem.fname}");
        }
    }
}
