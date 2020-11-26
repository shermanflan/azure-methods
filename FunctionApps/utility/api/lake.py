import logging
from os.path import split
from threading import Lock

from azure.core.exceptions import (ResourceNotFoundError,
                                   ResourceExistsError)
from azure.storage.filedatalake import DataLakeServiceClient


class DataLakeHook(object):
    """
    Data lake routines
    """
    def __init__(self, lake_url, lake_key):
        if not lake_url or not lake_key:
            raise Exception("Missing data lake credentials")

        self.__lake_url = lake_url
        self.__lake_key = lake_key
        self.__connection = None

    def __get_connection(self):
        """
        Reusable connection.

        :return: the DataLakeServiceClient client
        """
        if not self.__connection:
            logging.info(f'Authenticating to data lake...')

            self.__connection = DataLakeServiceClient(
                account_url=self.__lake_url,
                credential=self.__lake_key)

        return self.__connection

    def upload_files(self, lake_container, lake_dir, files):
        """
        Upload local files to lake.

        :param lake_container: lake container
        :param lake_dir: lake target path
        :param files: list of local file paths
        :return: None
        """
        lake_client = self.__get_connection()
        fs = lake_client.get_file_system_client(file_system=lake_container)
        dc = fs.get_directory_client(directory=lake_dir)

        try:
            dc.create_directory()
        except ResourceExistsError as e:
            logging.error(f'Lake container exists: {lake_container}')
        except ResourceNotFoundError as e:
            logging.error(f'Lake container does not exist: {lake_container}')
            raise

        for file in files:
            with open(file, 'rb') as f:
                _, tail = split(file)

                fc = dc.create_file(file=tail)
                data = f.read()
                fc.append_data(data, offset=0, length=len(data))
                fc.flush_data(len(data))

                logging.info(f'Uploaded to lake: {file} to {lake_dir}/{tail}')


    def upload_data(self, lake_container, lake_dir, file_name, data):
        """
        Upload in-memory data to lake.

        :param lake_container: lake container
        :param lake_dir: lake target path
        :param file_name: the target file name
        :param data: data bytes
        :return: None
        """
        lake_client = self.__get_connection()
        fs = lake_client.get_file_system_client(file_system=lake_container)
        dc = fs.get_directory_client(directory=lake_dir)

        try:
            dc.create_directory()
        except ResourceExistsError as e:
            logging.error(f'Lake container exists: {lake_container}')
        except ResourceNotFoundError as e:
            logging.error(f'Lake container does not exist: {lake_container}')
            raise
        
        # TODO: Iterative append
        # https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/storage/azure-storage-file-datalake/samples/datalake_samples_upload_download.py#L49
        fc = dc.create_file(file=file_name)
        fc.append_data(data, offset=0, length=len(data))
        fc.flush_data(len(data))

        logging.info(f'Uploaded to lake: {lake_dir}/{file_name}')