import logging

import requests
from requests.exceptions import HTTPError

from graph_api import GRAPH_API_ENDPOINT
import graph_api.logging

logger = logging.getLogger(__name__)

_DEBUG = True  # temp


def get_using_requests(token, limit=250,):
    """
    Example using native REST libraries.

    :param token:
    :param limit:
    :return: None
    """

    # Calling graph using the access token
    uri = f"{GRAPH_API_ENDPOINT}/users"
    headers = {'Authorization': f"Bearer {token}"}
    params = {
        '$top': f"{limit}",
        '$select': 'id,displayName,givenName,surname,userPrincipalName,' +
                   'jobTitle,companyName,department,officeLocation,' +
                   'employeeId,mail,onPremisesDomainName,createdDateTime'
    }

    try:
        users = requests.get(uri, headers=headers, params=params)
        users.raise_for_status()

        data = users.json()
        count = len(data['value'])  # limit

        # logger.debug(f"Graph API call result: {json.dumps(payload, indent=2)}")

        if '@odata.nextLink' in data:
            uri = data['@odata.nextLink']

            for data in get_next_users(uri, headers):
                count += len(data['value'])  # limit
                logger.debug(f'Retrieved: {count}')
                # sleep(1)

        logger.debug(f'Reached end of users request.')

    except HTTPError as e:
        logger.debug(f'Response Code: {users.status_code}')
        logger.exception(e)

        raise


def get_next_users(uri, headers):
    """
    TODO: Will iterator play nice with tenacity?

    :param uri:
    :param headers:
    :return: response payload as Dict
    """
    times = 4

    while True:

        users = requests.get(uri, headers=headers)
        users.raise_for_status()
        data = users.json()
        yield data

        if '@odata.nextLink' in data:
            uri = data['@odata.nextLink']
        else:
            break

        times -= 1

        if _DEBUG and not times:
            break

    return None
