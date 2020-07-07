using Microsoft.IdentityModel.Clients.ActiveDirectory;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Configuration;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Runtime;
using System.Threading.Tasks;
using System.Web;

namespace WhoAmI
{
    // TODO: Create a .NET core / Ubuntu image?
    public class Program
    {
        public static void Main(string[] args)
        {
            // Azure Active Directory registered app clientid for Microsoft samples
            string url = null;
            string tenantId = null;
            string clientId = null;
            string clientSecret = null;

            try
            {
                var appSettings = ConfigurationManager.AppSettings;

                if (appSettings.Count == 0)
                {
                    Console.WriteLine("AppSettings is empty.");
                    return;
                }

                url = appSettings["AADResource"];
                tenantId = appSettings["AADTenant"];
                //clientId = appSettings["AADClientMulti"];
                //clientSecret = appSettings["AADSecretMulti"];
                clientId = appSettings["AADClient"];
                clientSecret = appSettings["AADSecret"];

            }
            catch (ConfigurationErrorsException)
            {
                Console.WriteLine("Error reading app settings");
            }

            string authority = $"https://login.microsoftonline.com/{tenantId}";
            string apiVersion = "9.1";  // also, 9.0
            string webApiUrl = $"{url}/api/data/v{apiVersion}/";

            // Authenticate using IdentityModel.Clients.ActiveDirectory
            var clientCredential = new ClientCredential(clientId, clientSecret);
            var authContext = new AuthenticationContext(authority, false);
            var authResult = authContext.AcquireTokenAsync(url, clientCredential).Result;
            var authHeader = new AuthenticationHeaderValue("Bearer", authResult.AccessToken);

            var app = new Program();

            using (var client = new HttpClient())
            {
                client.BaseAddress = new Uri(webApiUrl);
                client.DefaultRequestHeaders.Authorization = authHeader;
                client.DefaultRequestHeaders.Add("Accept", "application/json");
                client.DefaultRequestHeaders.Add("OData-MaxVersion", "4.0");
                client.DefaultRequestHeaders.Add("OData-Version", "4.0");

                // GET: the WhoAmI function
                //app.GetWhoAmI(client);
                //Task t = app.GetWhoAmIAsync(client);
                //t.Wait();

                // GET: Patient (pah_patient)
                //app.GetPatient(client);

                // PATCH: Patient (pah_patient)
                app.UpdatePatient(client);

                // POST: Patient (pah_patient)
                //app.CreatePatient(client);

                // POST: Patient (pah_patient)
                //app.UpsertPatient(client);

                // DELETE: Patient (pah_patient)
                //app.DeletePatient(client);
            }

            Console.WriteLine("Press any key to exit.");
            Console.ReadLine();
        }

        public void GetWhoAmI(HttpClient client)
        {
            // GET: the WhoAmI function
            var response = client.GetAsync("WhoAmI").Result;

            if (response.IsSuccessStatusCode)
            {
                //Get the response content and parse it.  
                JObject body = JObject.Parse(response.Content.ReadAsStringAsync().Result);
                Guid userId = (Guid)body["UserId"];
                Console.WriteLine("Your UserId is {0}", userId);
                Console.WriteLine("Your OrganizationId is {0}", body["OrganizationId"]);
            }
            else
            {
                Console.WriteLine("The request failed with a status of '{0}'", response.ReasonPhrase);
            }
        }

        public async Task GetWhoAmIAsync(HttpClient client)
        {
            // GET: the WhoAmI function
            var response = await client.GetAsync("WhoAmI");

            if (response.IsSuccessStatusCode)
            {
                //Get the response content and parse it.
                var content = await response.Content.ReadAsStringAsync();
                JObject body = JObject.Parse(content);
                Guid userId = (Guid)body["UserId"];
                Console.WriteLine("Your UserId is {0}", userId);
                Console.WriteLine("Your OrganizationId is {0}", body["OrganizationId"]);
            }
            else
            {
                Console.WriteLine("The request failed with a status of '{0}'", response.ReasonPhrase);
            }
        }

        public void GetPatient(HttpClient client)
        {
            // Include formatted values (i.e. option sets).
            client.DefaultRequestHeaders.Add("Prefer", "odata.include-annotations=\"*\"");

            // GET: pah_patient
            //string query = HttpUtility.UrlEncode("$filter=pah_name eq 'John RKO Smith'");
            string query = "$filter=contains(pah_name,'RKO') or contains(pah_name,'John')";
            string resource = $"pah_patients?{query}";

            HttpResponseMessage response = client.GetAsync(resource).Result;

            if (response.IsSuccessStatusCode)
            {
                // Get the response content and parse it.
                var payload = response.Content.ReadAsStringAsync().Result;
                JObject body = JObject.Parse(payload);  // returns an array of patients

                foreach (var patient in body["value"])
                {
                    Console.WriteLine("pah_patientid: {0}", patient["pah_patientid"]);
                    Console.WriteLine("Your pah_name is {0}", patient["pah_name"]);
                    Console.WriteLine("Gender: {0}", patient["pah_gender@OData.Community.Display.V1.FormattedValue"]);
                    Console.WriteLine("Your pah_address1_telephone1 is {0}", patient["pah_address1_telephone1"]);
                }
            }
            else
            {
                Console.WriteLine("The request failed with a status of '{0}'", response.ReasonPhrase);
            }
        }

        public void UpdatePatient(HttpClient client)
        {
            // TODO: In order to update option sets, they should be converted to global.
            // Return updated values.
            client.DefaultRequestHeaders.Add("Prefer", "return=representation");

            // PATCH: pah_patient
            string patientId = "af2179a3-20ba-ea11-a812-000d3a33f3c3";
            string resource = $"pah_patients({patientId})";

            JObject patient = new JObject(
                new JProperty("emailaddress", "johnny5@mail.com"),
                new JProperty("pah_address1_line1", $"From windows: {DateTime.Now.ToString("HH:mm:ss.ffffzzz")}"),
                new JProperty("pah_address1_telephone1", "3241112222"),
                new JProperty("pah_birthdate", new DateTime(2020, 3, 20)),
                new JProperty("pah_gender", "804150000")
            );

            HttpRequestMessage patch = new HttpRequestMessage(new HttpMethod("PATCH"), resource);
            var jsonBody = new StringContent(JsonConvert.SerializeObject(patient));
            jsonBody.Headers.ContentType = new MediaTypeHeaderValue("application/json");
            patch.Content = jsonBody;

            HttpResponseMessage response = client.SendAsync(patch).Result;

            if (response.IsSuccessStatusCode)
            {
                // Get the response content and parse it.
                var payload = response.Content.ReadAsStringAsync().Result;
                JObject body = JObject.Parse(payload);  // returns an object

                Console.WriteLine("pah_patientid: {0}", body["pah_patientid"]);
                Console.WriteLine("pah_name: {0}", body["pah_name"]);
                Console.WriteLine("emailaddress: {0}", body["emailaddress"]);
                Console.WriteLine("pah_birthdate: {0}", body["pah_birthdate"]);
                Console.WriteLine("gender: {0}", body["pah_gender"]);
            }
            else
            {
                Console.WriteLine("The request failed with a status of '{0}'", response.ReasonPhrase);
            }
        }

        public void CreatePatient(HttpClient client)
        {
            // Return updated values.
            client.DefaultRequestHeaders.Add("Prefer", "return=representation");

            // POST: pah_patient
            string resource = $"pah_patients";

            JObject patient = new JObject(
                new JProperty("pah_name", "Saitama Sensei"),
                new JProperty("emailaddress", "johnny5@mail.com"),
                new JProperty("pah_address1_telephone1", "3241112222"),
                new JProperty("pah_birthdate", new DateTime(2020, 3, 20))
            );

            var jsonBody = new StringContent(JsonConvert.SerializeObject(patient));
            jsonBody.Headers.ContentType = new MediaTypeHeaderValue("application/json");

            HttpResponseMessage response = client.PostAsync(resource, jsonBody).Result;

            if (response.IsSuccessStatusCode)
            {
                // Get the response content and parse it.
                var payload = response.Content.ReadAsStringAsync().Result;
                JObject body = JObject.Parse(payload);  // returns an object

                Console.WriteLine("pah_patientid: {0}", body["pah_patientid"]);
                Console.WriteLine("pah_name: {0}", body["pah_name"]);
                Console.WriteLine("emailaddress: {0}", body["emailaddress"]);
                Console.WriteLine("pah_birthdate: {0}", body["pah_birthdate"]);
            }
            else
            {
                Console.WriteLine("The request failed with a status of '{0}'", response.ReasonPhrase);
            }
        }

        public void UpsertPatient(HttpClient client)
        {
            // Return updated values.
            client.DefaultRequestHeaders.Add("Prefer", "return=representation");

            // POST: pah_patient
            string resource = $"pah_patients";

            JObject patient = new JObject(
                new JProperty("pah_name", "Saitama Sensei"),
                new JProperty("emailaddress", "johnny5@mail.com"),
                new JProperty("pah_address1_telephone1", "3241112222"),
                new JProperty("pah_birthdate", new DateTime(2020, 3, 20))
            );

            var jsonBody = new StringContent(JsonConvert.SerializeObject(patient));
            jsonBody.Headers.ContentType = new MediaTypeHeaderValue("application/json");

            // Duplicate detection is off by default.
            // TODO: Duplicate detection rules need to be created first.
            jsonBody.Headers.Add("MSCRM.SuppressDuplicateDetection", "false");

            HttpResponseMessage response = client.PostAsync(resource, jsonBody).Result;

            if (response.IsSuccessStatusCode)
            {
                // Get the response content and parse it.
                var payload = response.Content.ReadAsStringAsync().Result;
                JObject body = JObject.Parse(payload);  // returns an object

                Console.WriteLine("pah_patientid: {0}", body["pah_patientid"]);
                Console.WriteLine("pah_name: {0}", body["pah_name"]);
                Console.WriteLine("emailaddress: {0}", body["emailaddress"]);
                Console.WriteLine("pah_birthdate: {0}", body["pah_birthdate"]);
            }
            else
            {
                Console.WriteLine("The request failed with a status of '{0}'", response.ReasonPhrase);
            }
        }

        public void DeletePatient(HttpClient client)
        {
            // Return deleted values.
            //client.DefaultRequestHeaders.Add("Prefer", "return=representation");

            // DELETE: pah_patient
            string patientId = "474651e9-deb7-ea11-a812-000d3a33f3c3";
            string resource = $"pah_patients({patientId})";

            HttpRequestMessage del = new HttpRequestMessage(new HttpMethod("DELETE"), resource);
            var jsonBody = new StringContent("");
            jsonBody.Headers.ContentType = new MediaTypeHeaderValue("application/json");
            del.Content = jsonBody;

            HttpResponseMessage response = client.SendAsync(del).Result;

            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine("Deleted '{0}'", patientId);
            }
            else
            {
                Console.WriteLine("The request failed with a status of '{0}'", response.ReasonPhrase);
            }
        }
    }
}
