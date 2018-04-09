using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Queue;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using UtilitiesPOC;

namespace ConsoleAppTester.AzureUtility
{
    public class AzQueue
    {
        private CloudStorageAccount storageAccount = null;
        private CloudQueueClient queueclient = null;
        private CloudQueue queue = null;

        public AzQueue(string cnxn)
        {
            Init(cnxn);
        }

        private void Init(string cnxn)
        {
            storageAccount = CloudStorageAccount.Parse(cnxn);
            queueclient = storageAccount.CreateCloudQueueClient();
            queue = queueclient.GetQueueReference("outqueuerko03");
        }

        public async Task CreateQueueMessages()
        {
            //queue.CreateIfNotExists();
            CloudQueueMessage message = null;

            for (int nQueueMessageIndex = 0; nQueueMessageIndex <= 5; nQueueMessageIndex++)
            {
                var m1 = new TypedQueueMessage
                {
                    fname = "rico",
                    lname = "guzman",
                    email = "r@g.c",
                    devicelist = Convert.ToString(nQueueMessageIndex)
                };

                var jsonM = JsonConvert.SerializeObject(m1);
                message = new CloudQueueMessage(jsonM);

                await queue.AddMessageAsync(message);

                Console.WriteLine($"PUT QUEUE: {jsonM}");
            }
        }

        public async void ReadQueueMessages()
        {
            CloudQueueMessage message = null;
            queue.FetchAttributes();

            int? numQ = queue.ApproximateMessageCount;

            while (true)
            {
                message = await queue.GetMessageAsync();

                if (message == null)
                    break;

                TypedQueueMessage m1 = JsonConvert.DeserializeObject<TypedQueueMessage>(message.AsString);

                Console.WriteLine($"READ QUEUE: {m1.fname} {m1.lname} {m1.email} {m1.devicelist}");

                await queue.DeleteMessageAsync(message);
            }
        }
    }

}
