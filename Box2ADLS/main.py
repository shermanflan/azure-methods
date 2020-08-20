from datetime import date
from os import environ
from os.path import join
from tempfile import TemporaryDirectory

from azure.storage.filedatalake import DataLakeServiceClient

from box2adls.auth.box_jwt import auth_jwt
from box2adls.logging import root_logger as logger
from box2adls.util.adls_lib import upload_files
from box2adls.util.box_lib import (check_or_create_collab, navigate,
                                   download_files)


if __name__ == '__main__':

    box_user_id = environ.get('BOX_USER_ID', '')
    box_folder_id = environ.get('BOX_FOLDER_ID', '')
    daily_folder = date.today().strftime('%d-%B')
    box_folder_path = join(environ.get('BOX_FOLDER_PATH',
                                       'data_source_01/folder_1/2020'),
                           f"{daily_folder}")
    folder_list = box_folder_path.split('/')[-1::-1]
    adls_account_name = environ.get('ADLS_ACCOUNT_NAME', 'pahintegrationstorage')
    adls_account_key = environ.get('ADLS_ACCOUNT_KEY',
                                  '')
    adls_url = f'https://{adls_account_name}.dfs.core.windows.net/'
    adls_container_name = environ.get('ADLS_CONTAINER_NAME', 'box-demo-01')
    adls_folder_path = environ.get('ADLS_FOLDER_PATH', 'fusion/box_downloads')
    upload_dir = join(adls_folder_path, daily_folder)

    logger.info("Authenticating to Box API...")

    # Login as both folder's app user and service user.
    box_client_app = auth_jwt(box_config=join('config', 'box_config.json'))
    box_client_user = auth_jwt(box_config=join('config', 'box_config.json'),
                               user_id=box_user_id)

    logger.info("Authenticating to ADLS...")

    adls_client = DataLakeServiceClient(account_url=adls_url,
                                        credential=adls_account_key)

    service_user = box_client_app.user().get()
    logger.debug(f"Box Service: {service_user.name}")

    # To access box folders, collaborations must be in place.
    root_folder = box_client_user.folder(folder_id=box_folder_id).get()

    logger.info(f"Verifying Box collaborations on '{root_folder.name}'")

    check_or_create_collab(box_folder=root_folder, box_user=service_user)

    logger.info(f"Navigating Box folder path '{box_folder_path}'...")

    box_root = box_client_app.folder('0').get()

    logger.debug(f'Box root "{box_root.name}"')

    parent = navigate(box_root, folder_list)

    if not parent:
        raise Exception(f'Daily folder "{daily_folder}" not found.')

    with TemporaryDirectory() as tmp_dir:

        logger.info(f'Downloading Box files from "{parent.name}"...')

        local_paths = download_files(box_folder=parent, local_dir=tmp_dir)

        logger.info(f'Uploading to ADLS "{upload_dir}"...')

        upload_files(adls_client, adls_container_name, adls_dir=upload_dir,
                     files=local_paths)

    logger.info(f"Process complete...")
