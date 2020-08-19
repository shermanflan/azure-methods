from datetime import date
from os import environ
from os.path import join
from tempfile import TemporaryDirectory

from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import ResourceNotFoundError

from box2adls.auth.box_jwt import auth_jwt
from box2adls.logging import root_logger as logger
from box2adls.util.box_lib import check_or_create_collab, navigate


if __name__ == '__main__':

    box_user_id = environ.get('BOX_USER_ID', '')
    box_folder_id = environ.get('BOX_FOLDER_ID', '')
    daily_folder = date.today().strftime('%d-%B')
    box_folder_path = join(environ.get('BOX_FOLDER_PATH',
                                       'data_source_01/folder_1/2020'),
                           f"{daily_folder}")
    adls_account_name = environ.get('ADLS_ACCOUNT_NAME', 'pahintegrationstorage')
    adls_account_key = environ.get('ADLS_ACCOUNT_KEY',
                                  '')
    adls_url = f'https://{adls_account_name}.dfs.core.windows.net/'
    adls_container_name = environ.get('ADLS_CONTAINER_NAME', 'box-demo-01')
    adls_folder_path = environ.get('ADLS_FOLDER_PATH', 'fusion/box_downloads')

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

    folder_list = box_folder_path.split('/')[-1::-1]

    box_root = box_client_app.folder('0').get()

    logger.debug(f'Box root {box_root.type} "{box_root.name}" ({box_root.id})')

    parent = navigate(box_root, folder_list)

    logger.info(f"Downloading Box files for {parent.name}...")

    items = parent.get_items()

    with adls_client.get_file_system_client(file_system=adls_container_name) as fs:
        upload_dir = join(adls_folder_path, daily_folder)
        dc = fs.get_directory_client(directory=upload_dir)

        try:
            dc.create_directory()
        except ResourceNotFoundError as e:
            logger.error(f"ADLS container '{adls_container_name}' does not exist.")
            raise

        for i in items:

            if i.type == 'file':
                with TemporaryDirectory() as tmp_dir:
                    download_dir = join(tmp_dir, i.name)

                    logger.info(f'Downloading Box {i.type}: "{download_dir}" ({i.id})')

                    with open(download_dir, 'wb') as f:
                        i.download_to(f)

                    logger.info(f"Uploading to ADLS {upload_dir}/{i.name}...")

                    with open(download_dir, 'rb') as f:

                        fc = dc.create_file(file=i.name)
                        data = f.read() # i.content()
                        fc.append_data(data, offset=0, length=len(data))
                        fc.flush_data(len(data))

    logger.info(f"Process complete...")
