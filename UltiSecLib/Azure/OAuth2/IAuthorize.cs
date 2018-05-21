using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Microsoft.IdentityModel.Clients.ActiveDirectory;

namespace UltiSecLib.Azure.OAuth2
{
    public interface IAuthorize
    {
        Task<AuthenticationResult> AcquireToken();

        void SignOut();
    }
}
