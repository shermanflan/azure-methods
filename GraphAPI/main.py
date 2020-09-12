import asyncio
from datetime import datetime
import logging
import json
from tempfile import TemporaryDirectory

from graph_api import (GRAPH_API_SCOPES, GRAPH_PAGE_SIZE, BLOB_CONTAINER,
                       BLOB_PATH, LAKE_CONTAINER, LAKE_PATH)
from graph_api.auth import OAuthFactory
from graph_api.api.blob import BlobFactory
from graph_api.api.graph import (get_users, get_delta_link, get_delta,
                                 get_delta_list)
from graph_api.api.lake import LakeFactory
from graph_api.util import load_from_path
import graph_api.util.log

logger = logging.getLogger(__name__)


if __name__ == '__main__':

    # TODO
    # Consider flat file output to parquet
    # Consider writing success/failure to Teams
    # Incorporate Key Vault, Application Insights
    # Create postman collection and add to git
    # Handle throttling: HTTP 429, Retry-After in response
    # Use $top with value < 20 to reduce throttling cost.
    #   https://docs.microsoft.com/en-us/azure/architecture/patterns/throttling
    # Handle server busy: HTTP 503/504, use exponential backoff
    # Handle bandwidth exceeded: HTTP 509, fatal
    # Generate a unique GUID and send it on each Microsoft Graph REST request.
    #   This will help Microsoft investigate any errors more easily if you need
    #   to report an issue with Microsoft Graph.
    #   On every request to Microsoft Graph, generate a unique GUID, send it in
    #   the client-request-id HTTP request header, and also log it in your
    #   application's logs.
    #   Always log the request-id, timestamp and x-ms-ags-diagnostic from the HTTP
    #   response headers. These, together with the client-request-id, are required
    #   when reporting issues in Stack Overflow or to Microsoft Support.
    # Handle any other retry-able errors:
    #   https://docs.microsoft.com/en-us/graph/errors

    with TemporaryDirectory() as tmp_dir:

        save_point_path = BlobFactory().download_to_file(container=BLOB_CONTAINER,
                                                         blob_path=BLOB_PATH,
                                                         tmp_dir=tmp_dir)

        graph_token = OAuthFactory().get_token(GRAPH_API_SCOPES)

        if not save_point_path:

            logger.info(f'Retrieving user snapshot from Graph.')

            user_file = get_users(token=graph_token, tmp_root=tmp_dir, limit=GRAPH_PAGE_SIZE)

            logger.info(f'Uploading user snapshot to lake.')

            LakeFactory().upload_files(lake_container=LAKE_CONTAINER,
                                       lake_dir=LAKE_PATH, files=[user_file])

            logger.info(f'Saving delta link to establish "sync from now".')

            delta_link = get_delta_link(token=graph_token)
            delta_link.update({'saved_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')})

            BlobFactory().upload(container=BLOB_CONTAINER, blob_path=BLOB_PATH,
                                 source=json.dumps(delta_link, indent=4))

        else:
            logger.info(f'Retrieving user delta from Graph.')

            delta_link = load_from_path(save_point_path)

            assert delta_link and '@odata.deltaLink' in delta_link, \
                "Unknown error: delta link not found."

            logger.info(f'Retrieving user delta (ids only) from Graph.')

            delta_link, ids = get_delta_list(token=graph_token,
                                             delta_link=delta_link['@odata.deltaLink'])

            if delta_link and ids:

                logger.info(f'Retrieving user delta from Graph.')

                user_file = get_delta(token=graph_token, user_list=ids, tmp_root=tmp_dir)

                logger.info(f'Uploading user delta to lake.')

                LakeFactory().upload_files(lake_container=LAKE_CONTAINER,
                                           lake_dir=LAKE_PATH, files=[user_file])

                delta_link.update({'saved_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')})

                BlobFactory().upload(container=BLOB_CONTAINER, blob_path=BLOB_PATH,
                                     source=json.dumps(delta_link, indent=4))

    logger.info(f'Completed successfully...')
