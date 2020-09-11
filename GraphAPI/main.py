import asyncio
from datetime import datetime
import logging
import json
from tempfile import TemporaryDirectory

from graph_api import (GRAPH_API_SCOPES, BLOB_CONTAINER, BLOB_PATH,
                       LAKE_CONTAINER, LAKE_PATH)
from graph_api.auth import OAuthFactory
from graph_api.api.blob import BlobFactory
from graph_api.api.graph import get_users, get_delta_link
from graph_api.api.lake import LakeFactory
from graph_api.util import load_from_path
import graph_api.util.log

logger = logging.getLogger(__name__)


if __name__ == '__main__':

    # TODO
    # Consider using subprocess/popen on bcp to sql or SqlAlchemy ORM
    #   https://docs.python.org/3/library/subprocess.html
    # Consider mounted volume to blob file system to persist delta link
    # Consider flat file output to json, csv, parquet
    # Consider writing success/failure to Teams
    # Incorporate Key Vault, Application Insights
    # Create postman collection and add to git
    # Add asynchronous I/O?
    #   https://docs.python.org/3/library/asyncio.html
    # Handle throttling: HTTP 429, Retry-After in response
    # Use $top with value < 20 to reduce throttling cost.
    #   https://docs.microsoft.com/en-us/azure/architecture/patterns/throttling
    # Handle server busy: HTTP 503/504, use exponential backoff
    # Handle bandwidth exceeded: HTTP 509, fatal
    # Use change tracking for delta updates to users after initial sync.
    #   https://docs.microsoft.com/en-us/graph/delta-query-users
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

            logger.info(f'Retrieving users snapshot from Graph.')

            user_file = get_users(token=graph_token, tmp_root=tmp_dir)

            logger.info(f'Uploading users snapshot to lake.')

            LakeFactory().upload_files(lake_container=LAKE_CONTAINER,
                                       lake_dir=LAKE_PATH, files=[user_file])

            logger.info(f'Syncing from now so getting baseline delta link.')

            delta_link = get_delta_link(token=graph_token)

            delta_link.update({
                'saved_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            })

            BlobFactory().upload(container=BLOB_CONTAINER, blob_path=BLOB_PATH,
                                 source=json.dumps(delta_link, indent=4))

            # try:
            #     asyncio.run(upload_blob_async(file=user_file))
            # except TypeError as e:
            #     logger.debug("Ignoring type error in await.")

        else:
            logger.info(f'Retrieving users delta from Graph.')

            delta_link = load_from_path(save_point_path)

            assert delta_link and '@odata.deltaLink' in delta_link, \
                "Unknown error: delta link not found."

            logger.debug(f"Delta link: {delta_link['@odata.deltaLink']}")

    logger.info(f'Completed successfully...')
