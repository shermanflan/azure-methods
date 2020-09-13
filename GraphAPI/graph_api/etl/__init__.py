from datetime import datetime
import json

from graph_api import (GRAPH_API_SCOPES, GRAPH_PAGE_SIZE, BLOB_CONTAINER,
                       BLOB_PATH, LAKE_CONTAINER, LAKE_PATH)
from graph_api.api.graph import (get_users, get_delta_link, get_delta,
                                 get_delta_list)
from graph_api.api.blob import BlobFactory
from graph_api.api.lake import LakeFactory
from graph_api.util import load_from_path
from graph_api.util.log import logger


class EtlOperations:

    def __init__(self):
        pass

    def load_snapshot(self, tmp_dir):
        """

        :param tmp_dir:
        :return: None
        """
        # TODO: Do retry here imperatively.
        user_file = get_users(tmp_root=tmp_dir, limit=GRAPH_PAGE_SIZE)

        logger.info(f'Uploading user snapshot to lake.')

        LakeFactory().upload_files(lake_container=LAKE_CONTAINER,
                                   lake_dir=LAKE_PATH, files=[user_file])

        logger.info(f'Saving delta link to establish "sync from now".')

        delta_link = get_delta_link()
        delta_link.update({'saved_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')})

        BlobFactory().upload(container=BLOB_CONTAINER, blob_path=BLOB_PATH,
                             source=json.dumps(delta_link, indent=4))

    def load_delta(self, save_point_path, tmp_dir):
        """

        :param save_point_path:
        :param tmp_dir:
        :return: None
        """
        delta_link = load_from_path(save_point_path)

        assert delta_link and '@odata.deltaLink' in delta_link, \
            "Unknown error: delta link not found."

        logger.info(f'Retrieving user delta (ids only) from Graph.')

        # TODO: Do retry here imperatively.
        delta_link, ids = get_delta_list(delta_link=delta_link['@odata.deltaLink'])

        if delta_link and ids:
            logger.info(f'Retrieving user delta from Graph.')

            # TODO: Do retry here imperatively.
            user_file = get_delta(user_list=ids, tmp_root=tmp_dir)

            logger.info(f'Uploading user delta to lake.')

            LakeFactory().upload_files(lake_container=LAKE_CONTAINER,
                                       lake_dir=LAKE_PATH, files=[user_file])

            delta_link.update({'saved_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')})

            BlobFactory().upload(container=BLOB_CONTAINER, blob_path=BLOB_PATH,
                                 source=json.dumps(delta_link, indent=4))
