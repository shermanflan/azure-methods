from os.path import join

from azure.storage.filedatalake import DataLakeServiceClient

from box2adls.auth.box_jwt import auth_jwt
from box2adls.etl import box_to_lake
from box2adls.logging import root_logger as logger
from box2adls.util.config import (BOX_USER, BOX_FOLDER, BOX_PATH,
                                  BOX_MASK, BOX_RENAME, LAKE_KEY,
                                  LAKE_URL, LAKE_CONTAINER, LAKE_PATH)
from box2adls.util.box import check_or_create_collab


if __name__ == '__main__':

    logger.info("Authenticating to Box...")

    # Login as both folder's app user and service user.
    box_client_app = auth_jwt(box_config=join('config', 'box_config.json'))
    box_client_user = auth_jwt(box_config=join('config', 'box_config.json'),
                               user_id=BOX_USER)

    logger.info("Authenticating to lake...")

    lake_service = DataLakeServiceClient(account_url=LAKE_URL,
                                         credential=LAKE_KEY)

    # To access box folders, collaborations must be in place.
    check_or_create_collab(box_user_client=box_client_user,
                           box_service_client=box_client_app,
                           box_folder_id=BOX_FOLDER)

    logger.debug(f"Box file mask: {BOX_MASK}")

    box_to_lake(box_client=box_client_app,
                source=BOX_PATH, source_mask=BOX_MASK,
                source_rename=BOX_RENAME,
                lake_client=lake_service, lake_root=LAKE_CONTAINER,
                target=LAKE_PATH)

    logger.info(f"Process complete...")
