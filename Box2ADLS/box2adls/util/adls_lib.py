from os.path import split

from azure.core.exceptions import ResourceNotFoundError

from box2adls.logging import root_logger as logger


def upload_files(adls_client, adls_container, adls_dir, files):
    """
    Upload local files to ADLS.

    :param adls_client: ADLS client
    :param adls_container: ADLS container
    :param adls_dir: ADLS target path
    :param files: list of local file paths
    :return: None
    """
    with adls_client.get_file_system_client(file_system=adls_container) as fs:
        dc = fs.get_directory_client(directory=adls_dir)

        try:
            dc.create_directory()
        except ResourceNotFoundError as e:
            logger.error(f'ADLS container "{adls_container}" does not exist.')
            raise

        for download in files:
            with open(download, 'rb') as f:
                _, tail = split(download)

                fc = dc.create_file(file=tail)
                data = f.read()  # i.content()
                fc.append_data(data, offset=0, length=len(data))
                fc.flush_data(len(data))

                logger.info(f'Uploaded ADLS "{adls_dir}/{tail}"...')
