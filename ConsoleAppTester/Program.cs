using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using ConsoleAppTester.AzureUtility;
using ConsoleAppTester.RESTUtility;
using UtilitiesPOC;

using System.Configuration;

namespace ConsoleAppTester
{
    public class Program
    {
        private static readonly string cnxn = ConfigurationManager.AppSettings["funappdemo"];
        private static readonly string busCnxn = ConfigurationManager.AppSettings["ServiceBusConnectionString"];
        private static readonly string code = ConfigurationManager.AppSettings["code"];

        public static void Main(string[] args)
        {
            // Read/Write to Azure Queue.
            //AzQueue azq = new AzQueue(cnxn);
            //azq.CreateQueueMessages().Wait();
            //azq.ReadQueueMessages();

            // Read/Write to Azure Blob.
            //AzBlob azb = new AzBlob(cnxn);
            //azb.CreateBlob().Wait();
            //Console.WriteLine($"FROM CLOUD: {azb.ReadBlob().Result}");

            // Read/Write to Azure Service Bus Queue
            AzServiceBus azb = new AzServiceBus(busCnxn);
            //azb.CreateQueueMessage().Wait();
            //var t = azb.ReadQueueMessage();
            //Console.WriteLine($"{t.Result.ToString()}");

            // Read/Write to Azure Service Bus Topic
            azb.CreateTopicMessage().Wait();
            //var t2 = azb.ReadTopicMessage();

            //Console.WriteLine($"{t2.Result.ToString()}");

            // Ex 1: Out of the box HttpClient.
            //var nn = new NativeNet();
            //nn.Ex1_HttpClient();

            // Ex 2: Out of the box HttpWebRequest.
            //nn.Ex2_WebRequestGET();
            //nn.Ex2_WebRequestPOST();

            // Ex 3: Out of the box WebClient.
            //nn.Ex3_WebClientGET().Wait();

            //var t3 = new ThirdParty();
            //Console.WriteLine($"RESTSHARP: {t3.Ex1_RestSharpGET()}");
            //Console.WriteLine($"Async RESTSHARP: {t3.Ex1_RestSharpGETAsync().Result}");

            Console.ReadLine();
        }
    }
}
