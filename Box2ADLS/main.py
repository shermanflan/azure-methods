from datetime import date
from os import environ
from os.path import join, split
from tempfile import TemporaryDirectory

from azure.storage.filedatalake import DataLakeServiceClient

from box2adls.auth.box_jwt import auth_jwt
from box2adls.logging import root_logger as logger
from box2adls.util.adls_lib import upload_files
from box2adls.util.box_lib import (check_or_create_collab, navigate,
                                   download_files)


def box_to_adls(box_client, source, adls_client, adls_root, target):
    """
    Routine which copies folders from Box to ADLS.
    
    :param box_client: box client with access to source folder
    :param source: box source path
    :param adls_client: ADLS client
    :param adls_root: ADLS container
    :param target: ADLS target path
    :return: None
    """
    box_root = box_client.folder('0').get()

    logger.info(f"Navigating Box path '{source}' on '{box_root.name}'")

    folders = source.split('/')[-1::-1]
    daily = navigate(box_root, folders)

    if not daily:
        raise Exception(f'Daily folder "{split(source)[1]}" not found.')

    with TemporaryDirectory() as tmp_dir:

        logger.info(f'Downloading Box files from "{daily.name}"...')

        local_paths = download_files(box_folder=daily, local_dir=tmp_dir)

        logger.info(f'Uploading to ADLS "{target}"...')

        upload_files(adls_client, adls_root, adls_dir=target,
                     files=local_paths)


if __name__ == '__main__':

    box_user_id = environ.get('BOX_USER_ID', '')
    box_folder_id = environ.get('BOX_FOLDER_ID', '')
    adls_account_name = environ.get('ADLS_ACCOUNT_NAME', 'pahintegrationstorage')
    adls_account_key = environ.get('ADLS_ACCOUNT_KEY',
                                   '')
    adls_url = f'https://{adls_account_name}.dfs.core.windows.net/'
    adls_container = environ.get('ADLS_CONTAINER_NAME', 'box-demo-01')
    adls_path = environ.get('ADLS_FOLDER_PATH', 'fusion/box_downloads')

    daily_folder = date.today().strftime('%d-%B')
    adls_dir = join(adls_path, daily_folder)

    logger.info("Authenticating to Box API...")

    # Login as both folder's app user and service user.
    box_client_app = auth_jwt(box_config=join('config', 'box_config.json'))
    box_client_user = auth_jwt(box_config=join('config', 'box_config.json'),
                               user_id=box_user_id)

    logger.info("Authenticating to ADLS...")

    adls_service = DataLakeServiceClient(account_url=adls_url,
                                         credential=adls_account_key)

    # To access box folders, collaborations must be in place.
    check_or_create_collab(box_user_client=box_client_user,
                           box_service_client=box_client_app,
                           box_folder_id=box_folder_id)

    box_dir = join(environ.get('BOX_FOLDER_PATH',
                               'data_source_01/folder_1/2020'),
                   f"{daily_folder}")

    box_to_adls(box_client=box_client_app, source=box_dir,
                adls_client=adls_service, adls_root=adls_container,
                target=adls_dir)

    logger.info(f"Process complete...")
