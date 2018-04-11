using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using ConsoleAppTester.AzureUtility;
using UtilitiesPOC;

using System.Configuration;

// Ex1
using System.Net.Http;
using System.Net.Http.Headers;
using Newtonsoft.Json;

// Ex2
using System.Net;
using System.IO;

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
            /*
            AzBlob azb = new AzBlob(cnxn);

            azb.CreateBlob().Wait();

            Console.WriteLine($"FROM CLOUD: {azb.ReadBlob().Result}");
            */

            // Ex 1: Out of the box HttpClient.
            Ex1_HttpClient();

            // Ex 2: Out of the box HttpWebRequest.
            //Ex2_WebRequestGET();
            //Ex2_WebRequestPOST();

            Console.ReadLine();
        }

        // https://docs.microsoft.com/en-us/dotnet/api/system.net.http.httpclient?view=netframework-4.7.1
        // TODO: POST
        private static void Ex1_HttpClient()
        {
            string baseURI = "https://funappdemo01.azurewebsites.net/api/VSRequestSecure";
            string paramsURI = "?code=KK7PkYJHMp2AaOQq7KxnQEkHNJapxMGOrNNaFnougtEEFCbx9HCF9w==&name=Ricardo%20Guzman";

            // Disposable
            using (HttpClient client = new HttpClient())
            {
                client.BaseAddress = new Uri(baseURI);

                HttpRequestHeaders headers = client.DefaultRequestHeaders;
                headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

                HttpResponseMessage response = client.GetAsync(paramsURI).Result;  // blocks

                if (response.IsSuccessStatusCode)
                {
                    string data = response.Content.ReadAsStringAsync().Result; // blocks
                    TypedQueueMessage m1 = JsonConvert.DeserializeObject<TypedQueueMessage>(data);

                    Console.WriteLine($"EX1: {m1.ToString()}");
                }
                else
                {
                    Console.WriteLine($"{response.StatusCode} ({response.ReasonPhrase})");
                }
            }
        }

        private static void Ex1_HttpClientPOST()
        {

        }

        // https://docs.microsoft.com/en-us/dotnet/api/system.net.httpwebrequest?view=netframework-4.7.1
        // TODO: Async
        // TODO: Implement conditional GET
        private static void Ex2_WebRequestGET()
        {
            string baseURI = "https://funappdemo01.azurewebsites.net/api/VSRequestSecure?code=KK7PkYJHMp2AaOQq7KxnQEkHNJapxMGOrNNaFnougtEEFCbx9HCF9w==&name=Ricardo%20Guzman%20Jr2";

            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(baseURI);
            request.Method = "GET"; // GET is default verb

            try
            {
                var webResponse = (HttpWebResponse)request.GetResponse();

                if (webResponse.StatusCode == HttpStatusCode.OK)
                {
                    using (Stream webStream = webResponse.GetResponseStream())
                    {
                        if (webStream != null)
                        {
                            using (StreamReader responseReader = new StreamReader(webStream))
                            {
                                string response = responseReader.ReadToEnd();

                                TypedQueueMessage m1 = JsonConvert.DeserializeObject<TypedQueueMessage>(response);

                                Console.WriteLine(m1);
                            }
                        }
                    }
                }
                else
                {
                    Console.WriteLine($"{webResponse.StatusCode}: {webResponse.StatusDescription}");
                }
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
            }
        }

        // TODO: Async
        private static void Ex2_WebRequestPOST()
        {
            string baseURI = "https://funappdemo01.azurewebsites.net/api/VSRequestSecure?code=KK7PkYJHMp2AaOQq7KxnQEkHNJapxMGOrNNaFnougtEEFCbx9HCF9w==";
            string body = "{\"name\":\"Ricardo Guzman Jr.\"}";

            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(baseURI);
            request.Method = "POST";
            request.ContentType = "application/json";
            request.ContentLength = body.Length;

            using (Stream webStream = request.GetRequestStream())
            {
                using (StreamWriter requestWriter = new StreamWriter(webStream, System.Text.Encoding.ASCII))
                {
                    requestWriter.Write(body);
                }
            }

            try
            {
                var webResponse = (HttpWebResponse)request.GetResponse();

                if (webResponse.StatusCode == HttpStatusCode.OK)
                {

                    using (Stream webStream = webResponse.GetResponseStream())
                    {
                        if (webStream != null)
                        {
                            using (StreamReader responseReader = new StreamReader(webStream))
                            {
                                string response = responseReader.ReadToEnd();

                                TypedQueueMessage m1 = JsonConvert.DeserializeObject<TypedQueueMessage>(response);

                                Console.WriteLine(m1);
                            }
                        }
                    }
                }
                else
                {
                    Console.WriteLine($"{webResponse.StatusCode}: {webResponse.StatusDescription}");
                }
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
            }
        }
    }
}
