import logging
from os import environ
from os.path import join

from azure.storage.filedatalake import DataLakeServiceClient
import redis

from box2adls.auth.box_jwt import auth_jwt
from box2adls.etl import EtlOperations
from box2adls.exceptions import FolderMissingError
import box2adls.logging
from box2adls import (SIMMER, BROKER_URL, BOX_CONFIG,
                      BOX_PATH, BOX_PATH2, BOX_MASK, BOX_MASK2,
                      BOX_RENAME, TAB_NAME_PREV, TAB_NAME_CURR,
                      TAB_NAME_NEXT, BOX_RENAME2, TAB_HIDDEN_NAME,
                      TAB_HIDDEN_RENAME,
                      LAKE_KEY, LAKE_URL, LAKE_CONTAINER, LAKE_PATH
                      )
from box2adls.util.box import check_or_create_collab


logger = logging.getLogger(__name__)

if __name__ == '__main__':

    if SIMMER:
        logger.info("Simulating error")

        r = redis.from_url(BROKER_URL)
        loop = r.incr(name='simmer', amount=1)

        if loop <= 3:
            raise FolderMissingError(f"Simulating error on try {loop-1}")

    logger.info("Authenticating to Box...")

    # Login as both folder's app user and service user.
    box_client_app = auth_jwt(box_config=BOX_CONFIG)
    # box_client_user = auth_jwt(box_config=join('config', 'box_config.json'),
    #                            user_id=BOX_USER)

    # To access box folders, collaborations must be in place.
    # check_or_create_collab(box_user_client=box_client_user,
    #                        box_service_client=box_client_app,
    #                        box_folder_id=BOX_FOLDER)

    logger.info("Authenticating to lake...")

    lake_service = DataLakeServiceClient(account_url=LAKE_URL,
                                         credential=LAKE_KEY)

    etl_ops = EtlOperations(box_client=box_client_app,
                            lake_client=lake_service,
                            lake_root=LAKE_CONTAINER, target=LAKE_PATH)

    logger.info("Pulling daily files...")
    etl_ops.daily_pull(source=BOX_PATH, source_mask=BOX_MASK,
                       source_rename=BOX_RENAME, prev_label=TAB_NAME_PREV,
                       curr_label=TAB_NAME_CURR, next_label=TAB_NAME_NEXT)

    logger.info("Pulling weekly files...")
    etl_ops.weekly_pull(source=BOX_PATH2, source_mask=BOX_MASK2,
                        source_rename=BOX_RENAME2, tab_name=TAB_HIDDEN_NAME,
                        tab_rename=TAB_HIDDEN_RENAME)

    logger.info(f"Process complete...")
