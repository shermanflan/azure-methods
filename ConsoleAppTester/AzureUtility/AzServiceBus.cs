using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Microsoft.ServiceBus.Messaging;
using Newtonsoft.Json;
using UtilitiesPOC;

namespace ConsoleAppTester.AzureUtility
{
    public class AzServiceBus
    {
        // Call Close() in destructor?
        private QueueClient queueClient = null;
        private TopicClient topicClient = null;
        private SubscriptionClient subsClient = null;
        private string queueName = "rkoqueue01";
        private string topicName = "rkotopic01";
        private string subscriptionName = "ConsoleAppTester";

        public AzServiceBus(string cnxn)
        {
            Init(cnxn);
        }

        private void Init(string cnxn)
        {
            queueClient = QueueClient.CreateFromConnectionString(cnxn, queueName);
            topicClient = TopicClient.CreateFromConnectionString(cnxn, topicName);
            subsClient = SubscriptionClient.CreateFromConnectionString(cnxn, topicName, subscriptionName);
        }

        /*
         * Service Bus Queue
         * TODO: Use this pattern.
         * https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dotnet-get-started-with-queues
         * 
         */
        public async Task CreateQueueMessage()
        {
            var m1 = new TypedQueueMessage
            {
                fname = "rico",
                lname = "guzman",
                email = "r@g.c",
                devicelist = "Queue test from console3"
            };

            var jsonM = JsonConvert.SerializeObject(m1);

            var message = new BrokeredMessage(jsonM);

            await queueClient.SendAsync(message);
        }

        public async Task<TypedQueueMessage> ReadQueueMessage()
        {
            Task<TypedQueueMessage> t1 = null;
            TypedQueueMessage m1 = null;

            queueClient.OnMessageAsync((msg) =>
            {
                t1 = Task<TypedQueueMessage>.Run(() =>
                {
                    var body = msg.GetBody<string>();
                    m1 = JsonConvert.DeserializeObject<TypedQueueMessage>(body);

                    return m1;
                });

                return t1;
            });

            return await t1;
        }

        /*
         * Service Bus Topic
         * TODO: Use this pattern.
         * https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dotnet-how-to-use-topics-subscriptions
         * 
         */
        public async Task CreateTopicMessage()
        {
            var m1 = new TypedQueueMessage
            {
                fname = "rico",
                lname = "guzman",
                email = "r@g.c",
                devicelist = "Topic test from console2"
            };

            var jsonM = JsonConvert.SerializeObject(m1);

            var message = new BrokeredMessage(jsonM);

            await topicClient.SendAsync(message);

        }

        public async Task<TypedQueueMessage> ReadTopicMessage()
        {
            Task<TypedQueueMessage> t1 = null;
            TypedQueueMessage m1 = null;

            subsClient.OnMessageAsync((msg) =>
            {
                t1 = Task<TypedQueueMessage>.Run(() =>
                {
                    var body = msg.GetBody<string>();
                    m1 = JsonConvert.DeserializeObject<TypedQueueMessage>(body);

                    return m1;
                });

                return t1;
            });

            return await t1;
        }
    }
}
