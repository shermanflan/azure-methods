import logging
from os.path import join, split
from threading import Lock

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

from graph_api import BLOB_URL, STORE_KEY
import graph_api.util.log

logger = logging.getLogger(__name__)


class BlobFactory(object):
    """
    Implementation of a singleton for managing blob resource.

    TODO:
    - Is this the best way to implement the singleton/factory pattern in Python?
    - Consider refactoring into a shared library.

    Inspired by:
    - https://github.com/Azure-Samples/azure-sql-db-python-rest-api

    """
    __instance = None
    __connection = None
    __lock = Lock()

    def __new__(cls):
        if BlobFactory.__instance is None:
            BlobFactory.__instance = object.__new__(cls)
        return BlobFactory.__instance

    def __get_connection(self):
        """
        Create a long-lived blob client.

        :return: the DataLakeServiceClient client
        """
        if not self.__connection:
            logger.info(f'Authenticating to data lake...')

            self.__connection = BlobServiceClient(account_url=BLOB_URL,
                                                  credential=STORE_KEY)

        return self.__connection

    def __remove_connection(self):
        self.__connection = None

    def get_blob_to_file(self, container, blob_path, tmp_dir):
        """
        TODO:
        - Write a streaming version.

        :param container:
        :param blob_path:
        :param tmp_dir:
        :return: The path to the downloaded blob or None.
        """
        service = self.__get_connection()

        container_client = service.get_container_client(container=container)

        try:
            container_client.create_container()
        except ResourceExistsError as e:
            logger.debug(f'Container exists, proceeding...')

        blob_client = container_client.get_blob_client(blob=blob_path)
        local_path = join(tmp_dir, split(blob_path)[1])

        try:
            with open(local_path, "wb") as file:
                data = blob_client.download_blob()
                data.readinto(file)

                return local_path
        except ResourceNotFoundError as e:
            logger.info(f'Last delta does not exist.')
            return None

    async def upload_blob_async(self, container, blob_path, file):
        """
        Async version.

        TODO: Need to understand asyncio
        - https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/storage/azure-storage-blob/samples/blob_samples_hello_world_async.py
        - https://stackoverflow.com/questions/33357233/when-to-use-and-when-not-to-use-python-3-5-await/33399896#33399896

        :param container:
        :param blob_path:
        :param file:
        :return:
        """
        service = self.__get_connection()

        # async with service:

        container_client = service.get_container_client(container=container)

        try:
            await container_client.create_container()
        except ResourceExistsError as e:
            logger.debug(f'Container exists.')

        blob_client = container_client.get_blob_client(blob=blob_path)

        with open(file, "rb") as data:
            await blob_client.upload_blob(data, overwrite=True)

    def upload_from_path(self, container, blob_path, file_path):
        """
        Sync version.

        :param container:
        :param blob_path:
        :param file_path:
        :return:
        """
        service = self.__get_connection()

        container_client = service.get_container_client(container=container)

        try:
            container_client.create_container()
        except ResourceExistsError as e:
            logger.debug(f'Container exists.')

        blob_client = container_client.get_blob_client(blob=blob_path)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

    def upload(self, container, blob_path, source):
        """
        Sync version.

        :param container:
        :param blob_path:
        :param source: 
        :return:
        """
        service = self.__get_connection()

        container_client = service.get_container_client(container=container)

        try:
            container_client.create_container()
        except ResourceExistsError as e:
            logger.debug(f'Container exists.')

        blob_client = container_client.get_blob_client(blob=blob_path)
        blob_client.upload_blob(source, overwrite=True)
