using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Queue;
using System.Configuration;

namespace ConsoleAppTester
{
    public class Program
    {
        public static void Main(string[] args)
        {
            CreateQueueMessages();

            Console.ReadLine();
        }

        private static void CreateQueueMessages()
        {
            string cnxn = ConfigurationManager.AppSettings["funappdemo"];
            CloudStorageAccount storageAccount = CloudStorageAccount.Parse(cnxn);
            CloudQueueClient queueclient = storageAccount.CreateCloudQueueClient();
            CloudQueue queue = queueclient.GetQueueReference("outqueuerko03");
            queue.CreateIfNotExists();
            CloudQueueMessage message = null;
            for (int nQueueMessageIndex = 0; nQueueMessageIndex <= 10; nQueueMessageIndex++)
            {
                message = new CloudQueueMessage(Convert.ToString(nQueueMessageIndex));
                queue.AddMessage(message);
                Console.WriteLine(nQueueMessageIndex);
            }
        }
    }
}
