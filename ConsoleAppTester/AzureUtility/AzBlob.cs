using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Blob;

namespace ConsoleAppTester.AzureUtility
{
    public class AzBlob
    {
        private CloudStorageAccount storageAccount = null;
        private CloudBlobClient blobClient = null;
        private CloudBlobContainer blobContainer = null;
        private CloudBlockBlob blob1 = null;
        private CloudBlockBlob blob2 = null;
        private CloudPageBlob blob3 = null;

        public AzBlob(string cnxn)
        {
            Init(cnxn);
        }

        private void Init(string cnxn)
        {
            storageAccount = CloudStorageAccount.Parse(cnxn);
            blobClient = storageAccount.CreateCloudBlobClient();
            blobContainer = blobClient.GetContainerReference("outcontainerimagesrko03");
            blob2 = blobContainer.GetBlockBlobReference("test01");
        }

        public async Task CreateBlob()
        {
            // TODO: Can also UploadFromStreamAsync(Stream)
            await blob2.UploadFromFileAsync(@"C:\Users\ricardogu\Desktop\Personal\Projects\Dynamics_Research\Scratch\src\data01.csv");
        }

        public async Task<string> ReadBlob()
        {
            // TODO: How to download from stream?
            blob1 = blobContainer.GetBlockBlobReference("test01");
            return await blob1.DownloadTextAsync();
        }

        // TODO: Delete, Move blob
    }
}
