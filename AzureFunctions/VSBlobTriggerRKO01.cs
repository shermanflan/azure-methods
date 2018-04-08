using System.IO;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Host;

namespace AzureFunctions
{
    public static class VSBlobTriggerRKO01
    {
        [FunctionName("VSBlobTriggerRKO01")]
        public static void Run(
            [BlobTrigger("outcontainerimagesrko03/{name}", Connection = "AzureWebJobsStorage")]Stream myBlob
            , string name, TraceWriter log)
        {
            log.Info($"C# Blob trigger function Processed blob\n Name:{name} \n Size: {myBlob.Length} Bytes");
        }
    }
}
