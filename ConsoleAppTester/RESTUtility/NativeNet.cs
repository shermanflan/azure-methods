using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using System.Net.Http;
using System.Net.Http.Headers;
using Newtonsoft.Json;
using UtilitiesPOC;
using System.Configuration;
using System.Net;
using System.IO;
using System.Collections.Specialized;

namespace ConsoleAppTester.RESTUtility
{
    /************************************************************************************
     * Native REST methods (no 3rd party software).
     ************************************************************************************/
    public class NativeNet
    {
        private static readonly string cnxn = ConfigurationManager.AppSettings["funappdemo"];
        private static readonly string code = ConfigurationManager.AppSettings["code"];

        /************************************************************************************
         * Ex1: HttpClient
         * The "new kid on the block" offers modern .NET functionalities that older libraries 
         * lack. .Net 4.5 and above.
         * 
         * https://docs.microsoft.com/en-us/dotnet/api/system.net.http.httpclient?view=netframework-4.7.1
         * 
         * TODO: Optimize: https://ankitvijay.net/2016/09/25/dispose-httpclient-or-have-a-static-instance/
         * TODO: Use IHttpFilter for Oauth/Oauth2
         ***********************************************************************************/

        public async void Ex1_HttpClient()
        {
            string baseURI = "https://funappdemo01.azurewebsites.net/api/VSRequestSecure";
            string paramsURI = $"?code={code}&name=Ricardo%20Guzman";

            // Disposable
            using (var client = new HttpClient())
            {
                client.BaseAddress = new Uri(baseURI);

                HttpRequestHeaders headers = client.DefaultRequestHeaders;
                headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36");
                headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

                HttpResponseMessage response = await client.GetAsync(paramsURI);  // blocks

                if (response.IsSuccessStatusCode)
                {
                    string data = await response.Content.ReadAsStringAsync(); // blocks
                    TypedQueueMessage m1 = JsonConvert.DeserializeObject<TypedQueueMessage>(data);

                    Console.WriteLine($"EX1: {m1.ToString()}");
                }
                else
                {
                    Console.WriteLine($"{response.StatusCode} ({response.ReasonPhrase})");
                }
            }
        }

        // TODO: POST
        public void Ex1_HttpClientPOST()
        {
            throw new NotImplementedException();
        }

        /************************************************************************************
         * Ex2: HttpWebRequest/HttpWebResponse
         * HTTP-specific implementation of WebRequest class which was originally used to deal 
         * with HTTP requests, but it was made obsolete and replaced by the WebClient class.
         * 
         * https://docs.microsoft.com/en-us/dotnet/api/system.net.httpwebrequest?view=netframework-4.7.1
         * TODO: Async
         * TODO: Implement conditional GET for web caching
         ************************************************************************************/

        public void Ex2_WebRequestGET()
        {
            string baseURI = $"https://funappdemo01.azurewebsites.net/api/VSRequestSecure?code={code}&name=Ricardo%20Guzman%20Jr2";

            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(baseURI);
            request.Method = "GET"; // GET is default verb

            try
            {
                var webResponse = (HttpWebResponse)request.GetResponse();

                if (webResponse.StatusCode == HttpStatusCode.OK)
                {
                    using (Stream webStream = webResponse.GetResponseStream())
                    {
                        using (StreamReader responseReader = new StreamReader(webStream))
                        {
                            string response = responseReader.ReadToEnd();

                            TypedQueueMessage m1 = JsonConvert.DeserializeObject<TypedQueueMessage>(response);

                            Console.WriteLine(m1);
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

        public void Ex2_WebRequestPOST()
        {
            string baseURI = $"https://funappdemo01.azurewebsites.net/api/VSRequestSecure?code={code}";
            string body = "{\"name\":\"Ricardo Guzman Jr.\"}";

            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(baseURI);
            request.Method = "POST";
            request.ContentType = "application/json";
            request.ContentLength = body.Length;

            using (Stream webStream = request.GetRequestStream())
            {
                using (StreamWriter requestWriter = new StreamWriter(webStream, Encoding.ASCII))
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
                        using (StreamReader responseReader = new StreamReader(webStream))
                        {
                            string response = responseReader.ReadToEnd();

                            TypedQueueMessage m1 = JsonConvert.DeserializeObject<TypedQueueMessage>(response);

                            Console.WriteLine(m1);
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

        /************************************************************************************
         * Ex3: WebClient
         * Wrapper around HttpWebRequest. If you want to write less code, not worry about all 
         * the details, and the execution speed is a non-factor, consider using WebClient class.
         * 
         * https://docs.microsoft.com/en-us/dotnet/api/system.net.webclient?view=netframework-4.7.1
         * 
         * TODO: POST
         ***********************************************************************************/
        public async Task<string> Ex3_WebClientGET()
        {
            string baseURI = "https://funappdemo01.azurewebsites.net/api/VSRequestSecure";

            var client = new WebClient();
            client.BaseAddress = baseURI;
            client.QueryString = new NameValueCollection()
            {
                { "code", $"{code}" }
                , { "name", "Ricardo%20Guzman2" }
            };
            client.Headers.Add("user-agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.0.3705;)");
            client.Headers.Add("Content-Type", "application/json");

            string response = await client.DownloadStringTaskAsync(baseURI);

            Console.WriteLine($"EX3: {JsonConvert.DeserializeObject<TypedQueueMessage>(response)}");
            return response;
        }
    }
}
