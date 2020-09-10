import logging
import json
import msal
from os.path import join
import requests

from graph_api import (AAD_ENDPOINT, APP_ID, APP_SECRET, GRAPH_API_SCOPES,
                       GRAPH_API_ENDPOINT)
import graph_api.util.log


# TODO
# Handle throttling: HTTP 429, Retry-After in response
# https://docs.microsoft.com/en-us/azure/architecture/patterns/throttling

# Use $top with value < 20 to reduce throttling cost.

# TODO
# Handle server busy: HTTP 503/504, use exponential backoff

# TODO
# Handle bandwidth exceeded: HTTP 509, fatal

# TODO
# Use change tracking for delta updates to users after initial sync.
# https://docs.microsoft.com/en-us/graph/delta-query-users

# TODO
# Implement singleton for connection resources
# https://github.com/Azure-Samples/azure-sql-db-python-rest-api/blob/master/app.py

# TODO
# Generate a unique GUID and send it on each Microsoft Graph REST request.
# This will help Microsoft investigate any errors more easily if you need
# to report an issue with Microsoft Graph.
# On every request to Microsoft Graph, generate a unique GUID, send it in
# the client-request-id HTTP request header, and also log it in your
# application's logs.
# Always log the request-id, timestamp and x-ms-ags-diagnostic from the HTTP
# response headers. These, together with the client-request-id, are required
# when reporting issues in Stack Overflow or to Microsoft Support.

logger = logging.getLogger(__name__)


def get_using_requests():
    """
    Example using native REST libraries.

    :return: None
    """
    # Create a preferably long-lived app instance which maintains a token cache.
    # You can learn how to use SerializableTokenCache from
    # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
    app = msal.ConfidentialClientApplication(client_id=APP_ID,
                                             client_credential=APP_SECRET,
                                             authority=AAD_ENDPOINT
                                             # token_cache=...  # Default cache is in memory only
                                             )

    # Firstly, looks up a token from cache
    # Since we are looking for token for the current app, NOT for an end user,
    # notice we give account parameter as None.
    result = app.acquire_token_silent(scopes=GRAPH_API_SCOPES, account=None)

    if not result:
        logger.info("No suitable token exists in cache. Let's get a new one from AAD.")
        result = app.acquire_token_for_client(scopes=GRAPH_API_SCOPES)

    if "access_token" in result:
        # Calling graph using the access token
        users = join(GRAPH_API_ENDPOINT, 'users')
        headers = {'Authorization': 'Bearer ' + result['access_token']}
        params = {'$filter': "startswith(displayName, 'Ricardo') and createdDateTime ge 2020-04-01"}

        graph_data = requests.get(users, headers=headers, params=params)

        logger.debug(f"Graph API call result: {json.dumps(graph_data.json(), indent=2)}")


if __name__ == '__main__':

    get_using_requests()

    logger.info(f'Completed successfully...')
