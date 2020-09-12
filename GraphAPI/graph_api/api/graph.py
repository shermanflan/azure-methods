import csv
from datetime import datetime
import logging
from os.path import join

import requests
from requests.exceptions import HTTPError

from graph_api import GRAPH_API_ENDPOINT, GRAPH_META
import graph_api.util.log

logger = logging.getLogger(__name__)


# Simple retry example:
#   https://github.com/microsoftgraph/msgraph-sdk-python-core/blob/dev/msgraphcore/middleware/authorization.py
# def send(self, request, **kwargs):
#     request.headers.update({'Authorization': 'Bearer {}'.format(self._get_access_token())})
#     response = super().send(request, **kwargs)
#
#     # Token might have expired just before transmission, retry the request one more time
#     if response.status_code == 401 and self.retry_count < 2:
#         self.retry_count += 1
#         return self.send(request, **kwargs)
#     return response


def get_users(token, tmp_root, limit=250):
    """
    Get initial user snapshot using REST and save to CSV. Uses
    session to promote connection reuse.

    :param token:
    :param tmp_root:
    :param limit:
    :return: full path to saved flat file
    """
    uri = f"{GRAPH_API_ENDPOINT}/users"
    headers = {'Authorization': f"Bearer {token}"}
    params = {'$top': f"{limit}", '$select': GRAPH_META}

    try:
        session = requests.Session()
        users = session.get(uri, headers=headers, params=params)
        users.raise_for_status()
        data = users.json()
    except HTTPError as e:
        logger.error(f'Initial response Code: {users.status_code}')
        logger.exception(e)

        raise

    file_stamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')
    tmp_path = join(tmp_root, f"{file_stamp}-user_snapshot.csv")

    with open(tmp_path, 'w', newline='') as csv_file:

        count = len(data['value'])

        if not count:
            logger.info('No user data found.')
            return

        writer = csv.DictWriter(csv_file, fieldnames=GRAPH_META.split(','))
        writer.writeheader()
        writer.writerows(data['value'])

        while True:

            if '@odata.nextLink' in data:
                uri = data['@odata.nextLink']
                data = _get_next_users(session, uri, headers)

                count += len(data['value'])

                writer.writerows(data['value'])

                logger.debug(f'{count} snapshot rows written.')
            else:
                break

    return tmp_path


def _get_next_users(session, uri, headers):
    """
    Reuses the request connection for efficiency.

    :param session:
    :param uri:
    :param headers:
    :return: response payload as Dict
    """
    try:
        users = session.get(uri, headers=headers)
        users.raise_for_status()

        return users.json()
    except HTTPError as e:
        logger.error(f'Delta response Code: {users.status_code}')
        logger.exception(e)

        raise

# Simple generator example from:
# https://github.com/microsoftgraph/python-sample-pagination/blob/master/generator.py
# def graph_generator(session, endpoint=None):
#     while endpoint:
#         print('Retrieving next page ...')
#         response = session.get(endpoint).json()
#         yield from response.get('value')
#         endpoint = response.get('@odata.nextLink')


def get_delta_link(token):
    """
    Establishes the "sync from now" checkpoint and retrieves the first
    delta link.

    Uses change tracking for delta updates to users after initial sync.
    See:
    - https://docs.microsoft.com/en-us/graph/delta-query-users

    :param token:
    :return: the Dict containing first users delta link.
    """
    uri = f"{GRAPH_API_ENDPOINT}/users/delta"
    headers = {'Authorization': f"Bearer {token}"}
    params = {
        '$deltaToken': "latest",
        '$select': GRAPH_META
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


def get_delta_list(token, delta_link):
    """
    Get delta of users since last delta link (id's only).

    Uses change tracking for delta updates to users after initial sync.
    See:
    - https://docs.microsoft.com/en-us/graph/delta-query-users

    :param token:
    :param delta_link:
    :return: List of user ids.
    """
    headers = {'Authorization': f"Bearer {token}"}

    try:
        session = requests.Session()
        users = session.get(delta_link, headers=headers)
        users.raise_for_status()
        data = users.json()
    except HTTPError as e:
        logger.error(f'Initial response Code: {users.status_code}')
        logger.exception(e)

        raise

    if not data['value']:
        logger.info('No user deltas exist.')
        return None, []

    user_ids = [u['id'] for u in data['value']]

    while True:

        if '@odata.nextLink' in data:
            uri = data['@odata.nextLink']
            data = _get_next_delta(session, uri, headers)

            user_ids.extend([u['id'] for u in data['value']])

        elif '@odata.deltaLink' in data:

            logger.info(f'Collected {len(user_ids)} users, getting next delta link.')
            del data['value']

            return data, user_ids
        else:
            break

    raise Exception(f'Unknown error condition, no next or delta link.')


def _get_next_delta(session, uri, headers):
    """
    Reuses the request connection via shared Session for efficiency.

    :param session
    :param uri:
    :param headers:
    :return: response payload as Dict
    """

    try:
        users = session.get(uri, headers=headers)
        users.raise_for_status()
        data = users.json()

        if '@odata.nextLink' in data or '@odata.deltaLink' in data:
            return data

    except HTTPError as e:
        logger.error(f'Delta response Code: {users.status_code}')
        logger.exception(e)

        raise

    raise Exception(f'Unknown error condition, no next or delta link.')


def get_delta(token, user_list, tmp_root):
    """
    Get list users as specified in given list of ids.

    Uses change tracking for delta updates to users after initial sync.
    See:
    - https://docs.microsoft.com/en-us/graph/delta-query-users

    :param token:
    :param user_list:
    :param tmp_root:
    :return:
    """
    file_stamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')
    tmp_path = join(tmp_root, f"{file_stamp}-user_delta.csv")

    with open(tmp_path, 'w', newline='') as csv_file:

        writer = csv.DictWriter(csv_file, fieldnames=GRAPH_META.split(','))
        writer.writeheader()

        headers = {'Authorization': f"Bearer {token}"}
        params = {'$select': GRAPH_META}
        session = requests.Session()

        for u in user_list:
            uri = f"{GRAPH_API_ENDPOINT}/users/{u}"

            try:
                user_list = session.get(uri, headers=headers, params=params)
                user_list.raise_for_status()
                data = user_list.json()

                if data:
                    del data['@odata.context']
                    writer.writerow(data)
            except HTTPError as e:
                logger.error(f'Initial response Code: {user_list.status_code}')

                if user_list.status_code == 404:
                    logger.error(f'User {u} not found. Skipping...')
                    continue

                logger.exception(e)

                raise

        return tmp_path
