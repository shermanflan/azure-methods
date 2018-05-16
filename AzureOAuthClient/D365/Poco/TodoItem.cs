using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AzureOAuthClient.D365.Poco
{
    public class TodoItem
    {
        public string Title { get; set; }
        public string Owner { get; set; }

        public override string ToString()
        {
            return String.Format($"{Title} {Owner}");
        }
    }

}
