import logging
import json
import msal
from os.path import join
import requests
from requests.exceptions import HTTPError
from time import sleep

from graph_api import (AAD_ENDPOINT, APP_ID, APP_SECRET, GRAPH_API_SCOPES,
                       GRAPH_API_ENDPOINT)
import graph_api.util.log

logger = logging.getLogger(__name__)


def get_using_requests(limit=500):
    """
    Example using native REST libraries.

    :param limit:
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
        uri = join(GRAPH_API_ENDPOINT, 'users')
        headers = {'Authorization': 'Bearer ' + result['access_token']}
        params = {'$top': f"{limit}"}

        try:
            users = requests.get(uri, headers=headers, params=params)
            users.raise_for_status()

            data = users.json()
            count = len(data['value']) # limit

            # logger.debug(f"Graph API call result: {json.dumps(payload, indent=2)}")

            if '@odata.nextLink' in data:
                uri = data['@odata.nextLink']

                for data in get_next_users(uri, headers):
                    count += len(data['value'])  # limit
                    logger.debug(f'Retrieved: {count}')
                    sleep(1)

                logger.debug(f'Reached end of users request.')

        except HTTPError as e:
            logger.debug(f'Response Status: {users.status_code}')
            logger.exception(e)

            raise


def get_next_users(uri, headers):
    """
    TODO: Will iterator play nice with tenacity?

    :param uri:
    :param headers:
    :return: response payload as Dict
    """
    while True:

        users = requests.get(uri, headers=headers)
        users.raise_for_status()
        data = users.json()
        yield data

        if '@odata.nextLink' in data:
            uri = data['@odata.nextLink']
        else:
            break

    return None


if __name__ == '__main__':

    # TODO
    # Consider using process open on bcp to sql
    # Consider mounted volume to blob file system to persist delta link
    # Consider flat file output to json, csv, parquet

    get_using_requests()

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
    # Implement singleton/factory for connection resources
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

    logger.info(f'Completed successfully...')
