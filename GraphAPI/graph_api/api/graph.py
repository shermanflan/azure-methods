import csv
from datetime import datetime
from os.path import join

import requests
from requests.exceptions import HTTPError

from graph_api import GRAPH_API_ENDPOINT, GRAPH_API_SCOPES
from graph_api.auth import OAuthFactory
from graph_api.exceptions import RetryableError
from graph_api.util.log import get_logger

logger = get_logger(__name__)


def _raise_backoff(method):
    def handler(**kwargs):
        """
        Redo exception handling based on backoff/retry.

        :return:
        """
        try:
            return method(**kwargs)
        except HTTPError as e:
            logger.error(f'HTTP response code: {e.response.status_code}')
            logger.exception(e)

            if e.response.status_code in (429, 503, 504):
                logger.error(f"Server overloaded: Backing off...")

                delay = e.response.headers.get("Retry-After", None)
                if delay:
                    try:
                        raise RetryableError(f"Retry-after: {delay}.",
                                             retry_after=int(delay))
                    except (ValueError, TypeError):
                        pass

                raise RetryableError(f"Retry exponential backoff.",
                                     retry_after=None)
            raise

    return handler


@_raise_backoff
def get_users(tmp_root, columns, limit=250):
    """
    Get initial user snapshot using REST and save to CSV. Uses
    session to promote connection reuse.

    :param tmp_root:
    :param columns:
    :param limit:
    :return: full path to saved flat file
    """
    session = requests.Session()
    token = OAuthFactory().get_token(GRAPH_API_SCOPES)
    uri = f"{GRAPH_API_ENDPOINT}/users"
    headers = {'Authorization': f"Bearer {token}"}
    params = {'$top': f"{limit}", '$select': columns}

    file_stamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')
    tmp_path = join(tmp_root, f"{file_stamp}-user_snapshot.csv")

    with open(tmp_path, 'w', newline='') as csv_file:

        writer = csv.DictWriter(csv_file, fieldnames=columns.split(','))
        writer.writeheader()
        count = 0

        while uri:

            users = session.get(uri, headers=headers, params=params)
            users.raise_for_status()
            data = users.json()

            writer.writerows(data['value'])

            count += len(data['value'])
            logger.debug(f"{count} snapshot rows written.")

            uri = data.get('@odata.nextLink')
            params = None

    return tmp_path


@_raise_backoff
def get_delta_link(columns):
    """
    Establishes the "sync from now" checkpoint and retrieves the first
    delta link. Uses change tracking for delta updates to users after
    initial sync.

    See:
    - https://docs.microsoft.com/en-us/graph/delta-query-users

    :param columns:
    :return: the Dict containing first users delta link.
    """
    token = OAuthFactory().get_token(GRAPH_API_SCOPES)
    uri = f"{GRAPH_API_ENDPOINT}/users/delta"
    headers = {'Authorization': f"Bearer {token}"}
    params = {'$deltaToken': "latest", '$select': columns}

    delta = requests.get(uri, headers=headers, params=params)
    delta.raise_for_status()
    delta_link = delta.json()

    assert '@odata.deltaLink' in delta_link, \
        "Error: Delta link does not exist."

    return delta_link


@_raise_backoff
def get_delta_list(uri):
    """
    Get delta of users since last delta link (id's only). Uses
    change tracking for delta updates to users after initial sync.

    See:
    - https://docs.microsoft.com/en-us/graph/delta-query-users

    :param uri:
    :return: List of user ids.
    """
    session = requests.Session()
    token = OAuthFactory().get_token(GRAPH_API_SCOPES)
    headers = {'Authorization': f"Bearer {token}"}
    user_ids = []

    while uri:

        users = session.get(uri, headers=headers)
        users.raise_for_status()
        data = users.json()

        user_ids.extend([u['id'] for u in data['value']])
        uri = data.get('@odata.nextLink')

    assert '@odata.deltaLink' in data, "Error: Missing delta link."
    logger.info(f'Collected {len(user_ids)} user ids.')

    return data, user_ids


@_raise_backoff
def get_delta(user_list, columns, tmp_root):
    """
    Get list of users as specified in given list of ids. Uses
    change tracking for delta updates to users after initial sync.

    See:
    - https://docs.microsoft.com/en-us/graph/delta-query-users

    :param user_list:
    :param columns:
    :param tmp_root:
    :return:
    """
    file_stamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')
    tmp_path = join(tmp_root, f"{file_stamp}-user_delta.csv")

    with open(tmp_path, 'w', newline='') as csv_file:

        session = requests.Session()
        token = OAuthFactory().get_token(GRAPH_API_SCOPES)
        headers = {'Authorization': f"Bearer {token}"}
        params = {'$select': columns}

        writer = csv.DictWriter(csv_file, fieldnames=columns.split(','))
        writer.writeheader()

        for u in user_list:
            try:
                uri = f"{GRAPH_API_ENDPOINT}/users/{u}"
                user_list = session.get(uri, headers=headers, params=params)
                user_list.raise_for_status()

                data = user_list.json()
                del data['@odata.context']

                writer.writerow(data)
            except HTTPError as e:

                if user_list.status_code == 404:
                    logger.error(f"User '{u}' not found. Skipping...")
                    continue
                raise

        return tmp_path
