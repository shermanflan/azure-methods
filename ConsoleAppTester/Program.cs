using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using System.Configuration;

using ConsoleAppTester.AzureUtility;

namespace ConsoleAppTester
{
    public class Program
    {
        private static readonly string cnxn = ConfigurationManager.AppSettings["funappdemo"];

        public static void Main(string[] args)
        {
            // Read/Write to Azure Queue.
            /*
            AzQueue azq = new AzQueue(cnxn);

            azq.CreateQueueMessages().Wait();
            azq.ReadQueueMessages();
            */

            // Read/Write to Azure Blob.
            AzBlob azb = new AzBlob(cnxn);

            azb.CreateBlob().Wait();

            Console.WriteLine($"FROM CLOUD: {azb.ReadBlob().Result}");

            Console.ReadLine();
        }
    }
}
