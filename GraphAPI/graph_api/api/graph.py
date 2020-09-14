import csv
from datetime import datetime
from os.path import join

import requests
from requests.exceptions import HTTPError

from graph_api import (GRAPH_API_ENDPOINT, GRAPH_META,
                       GRAPH_API_SCOPES)
from graph_api.auth import OAuthFactory
from graph_api.exceptions import RetryableError
from graph_api.util.log import get_logger

logger = get_logger(__name__)


def get_users(tmp_root, limit=250):
    """
    Get initial user snapshot using REST and save to CSV. Uses
    session to promote connection reuse.

    :param tmp_root:
    :param limit:
    :return: full path to saved flat file
    """
    session = requests.Session()
    token = OAuthFactory().get_token(GRAPH_API_SCOPES)
    uri = f"{GRAPH_API_ENDPOINT}/users"
    headers = {'Authorization': f"Bearer {token}"}
    params = {'$top': f"{limit}", '$select': GRAPH_META}
    file_stamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')
    tmp_path = join(tmp_root, f"{file_stamp}-user_snapshot.csv")

    with open(tmp_path, 'w', newline='') as csv_file:

        writer = csv.DictWriter(csv_file, fieldnames=GRAPH_META.split(','))
        writer.writeheader()
        count = 0

        while uri:

            try:
                users = session.get(uri, headers=headers, params=params)
                users.raise_for_status()
                data = users.json()

                writer.writerows(data['value'])

                count += len(data['value'])
                logger.debug(f"{count} snapshot rows written.")

                uri = data.get('@odata.nextLink')
                params = None

            except HTTPError as e:
                logger.error(f'Initial response Code: {users.status_code}')
                logger.exception(e)

                if users.status_code in (429, 503, 504):
                    logger.error(f"Server overloaded: Backing off...")

                    try:
                        valid_delay = int(users.headers.get("Retry-After"))
                        raise RetryableError(f"Retry-after: {valid_delay}.",
                                             retry_after=valid_delay)
                    except (ValueError, TypeError):
                        raise RetryableError(f"Retry exponential backoff.",
                                             retry_after=None)

    return tmp_path


def get_delta_link():
    """
    Establishes the "sync from now" checkpoint and retrieves the first
    delta link.

    Uses change tracking for delta updates to users after initial sync.
    See:
    - https://docs.microsoft.com/en-us/graph/delta-query-users

    :return: the Dict containing first users delta link.
    """
    token = OAuthFactory().get_token(GRAPH_API_SCOPES)
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

        assert '@odata.deltaLink' in delta_link, \
            "Error: Delta link does not exist."

        return delta_link

    except HTTPError as e:
        logger.debug(f'Response Code: {delta.status_code}')
        logger.exception(e)

        if delta.status_code in (429, 503, 504):
            logger.error(f"Server overloaded: Backing off...")

            try:
                valid_delay = int(delta.headers.get("Retry-After"))
                raise RetryableError(f"Retry-after: {valid_delay}.",
                                     retry_after=valid_delay)
            except (ValueError, TypeError):
                raise RetryableError(f"Retry exponential backoff.",
                                     retry_after=None)

        raise


def get_delta_list(uri):
    """
    Get delta of users since last delta link (id's only).

    Uses change tracking for delta updates to users after initial sync.
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

        try:
            users = session.get(uri, headers=headers)
            users.raise_for_status()
            data = users.json()

            user_ids.extend([u['id'] for u in data['value']])
            uri = data.get('@odata.nextLink')
            
        except HTTPError as e:
            logger.error(f'Initial response Code: {users.status_code}')
            logger.exception(e)

            if users.status_code in (429, 503, 504):
                logger.error(f"Server overloaded: Backing off...")

                try:
                    valid_delay = int(users.headers.get("Retry-After"))
                    raise RetryableError(f"Retry-after: {valid_delay}.",
                                         retry_after=valid_delay)
                except (ValueError, TypeError):
                    raise RetryableError(f"Retry exponential backoff.",
                                         retry_after=None)

            raise

    assert '@odata.deltaLink' in data, "Error: Missing delta link."
    logger.info(f'Collected {len(user_ids)} user ids.')

    return data, user_ids


def get_delta(user_list, tmp_root):
    """
    Get list users as specified in given list of ids.

    Uses change tracking for delta updates to users after initial sync.
    See:
    - https://docs.microsoft.com/en-us/graph/delta-query-users

    :param user_list:
    :param tmp_root:
    :return:
    """
    file_stamp = datetime.now().strftime('%Y%m%d_%H%M%S.%f')
    tmp_path = join(tmp_root, f"{file_stamp}-user_delta.csv")

    with open(tmp_path, 'w', newline='') as csv_file:

        session = requests.Session()
        token = OAuthFactory().get_token(GRAPH_API_SCOPES)
        headers = {'Authorization': f"Bearer {token}"}
        params = {'$select': GRAPH_META}

        writer = csv.DictWriter(csv_file, fieldnames=GRAPH_META.split(','))
        writer.writeheader()

        for u in user_list:
            uri = f"{GRAPH_API_ENDPOINT}/users/{u}"

            try:
                user_list = session.get(uri, headers=headers, params=params)
                user_list.raise_for_status()

                data = user_list.json()
                del data['@odata.context']

                writer.writerow(data)
            except HTTPError as e:
                logger.error(f'Initial response Code: {user_list.status_code}')
                logger.exception(e)

                if user_list.status_code == 404:
                    logger.error(f"User '{u}' not found. Skipping...")
                    continue

                if user_list.status_code in (429, 503, 504):
                    logger.error(f"Server overloaded: Backing off...")

                    try:
                        valid_delay = int(user_list.headers.get("Retry-After"))
                        raise RetryableError(f"Retry-after: {valid_delay}.",
                                             retry_after=valid_delay)
                    except (ValueError, TypeError):
                        raise RetryableError(f"Retry exponential backoff.",
                                             retry_after=None)

                raise

        return tmp_path
