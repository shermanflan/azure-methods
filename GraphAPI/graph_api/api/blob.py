import logging

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient

from graph_api import BLOB_URL, STORE_KEY
import graph_api.logging

logger = logging.getLogger(__name__)


async def upload_blob_async(file):
    """
    Async version.

    TODO: Need to understand asyncio
    - https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/storage/azure-storage-blob/samples/blob_samples_hello_world_async.py
    - https://stackoverflow.com/questions/33357233/when-to-use-and-when-not-to-use-python-3-5-await/33399896#33399896

    :param file:
    :return:
    """
    service = BlobServiceClient(account_url=BLOB_URL, credential=STORE_KEY)

    # async with service:

    container_client = service.get_container_client(container='python-app-data')

    try:
        await container_client.create_container()
    except ResourceExistsError as e:
        logger.debug(f'Container exists.')

    blob_client = container_client.get_blob_client(blob='graph-api/next_delta.json')

    with open(file, "rb") as data:
        await blob_client.upload_blob(data, overwrite=True)


def upload_blob(file):
    """
    Sync version.

    TODO: Need to understand asyncio
    - https://stackoverflow.com/questions/33357233/when-to-use-and-when-not-to-use-python-3-5-await/33399896#33399896

    :param file:
    :return:
    """
    service = BlobServiceClient(account_url=BLOB_URL, credential=STORE_KEY)

    container_client = service.get_container_client(container='python-app-data')

    try:
        container_client.create_container()
    except ResourceExistsError as e:
        logger.debug(f'Container exists.')

    blob_client = container_client.get_blob_client(blob='graph-api/next_delta.json')

    with open(file, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
