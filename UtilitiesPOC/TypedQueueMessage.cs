using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UtilitiesPOC
{
    public class TypedQueueMessage
    {
        public string fname { get; set; }
        public string lname { get; set; }
        public string email { get; set; }
        public string devicelist { get; set; }

        public override string ToString()
        {
            return $"{fname} {lname} {email} {devicelist}";
        }
    }
}
