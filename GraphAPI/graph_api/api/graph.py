import csv
from datetime import datetime
import logging
from os.path import join
from threading import Lock

import requests
from requests.exceptions import HTTPError

from graph_api import GRAPH_API_ENDPOINT
import graph_api.util.log

logger = logging.getLogger(__name__)

_DEBUG = True  # temp


def get_users(token, tmp_root, limit=250):
    """
    Get initial user snapshot using REST and save to CSV.

    :param token:
    :param tmp_root:
    :param limit:
    :return: full path to saved flat file
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

        file_stamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')
        tmp_path = join(tmp_root, f"user_delta-{file_stamp}.csv")

        with open(tmp_path, 'w', newline='') as csv_file:

            data = users.json()
            count = len(data['value'])  # limit

            if not count:
                logger.info('No user data found.')
                return

            fields = data['value'][0].keys()
            writer = csv.DictWriter(csv_file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data['value'])

            if '@odata.nextLink' in data:
                uri = data['@odata.nextLink']

                for data in get_next_users(uri, headers):

                    count += len(data['value'])  # limit
                    logger.debug(f'Retrieved: {count}')

                    writer.writerows(data['value'])

        logger.debug(f'Reached end of users request.')

        return tmp_path

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
    times = 4  # tmp

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

        if _DEBUG and not times:  # tmp
            break

    return None


def get_delta_link(token):
    """
    Establishes the "sync from now" checkpoint and retrieves the first
    delta link.

    :param token:
    :return: the Dict containing first users delta link.
    """
    # Calling graph using the access token
    uri = f"{GRAPH_API_ENDPOINT}/users/delta"
    headers = {'Authorization': f"Bearer {token}"}
    params = {
        '$deltaToken': "latest",
        '$select': 'id,displayName,givenName,surname,userPrincipalName,' +
                   'jobTitle,companyName,department,officeLocation,' +
                   'employeeId,mail,onPremisesDomainName,createdDateTime'
    }

    try:
        delta = requests.get(uri, headers=headers, params=params)
        delta.raise_for_status()

        delta_link = delta.json()

        if '@odata.deltaLink' in delta_link:
            return delta_link
        else:
            raise Exception(f"Unknown error status: could not get delta link.")

    except HTTPError as e:
        logger.debug(f'Response Code: {delta.status_code}')
        logger.exception(e)

        raise


def get_next_delta(token):
    # TODO: get list of user ids, then collect from REST.
    pass
