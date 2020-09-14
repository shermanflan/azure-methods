from datetime import datetime
import json
from time import sleep

from graph_api import (GRAPH_PAGE_SIZE, BLOB_CONTAINER,
                       BLOB_PATH, LAKE_CONTAINER, LAKE_PATH)
from graph_api.api.graph import (get_users, get_delta_link, get_delta,
                                 get_delta_list)
from graph_api.api.blob import BlobFactory
from graph_api.api.lake import LakeFactory
from graph_api.exceptions import RetryableError, RetryExceededError
from graph_api.util import load_from_path
from graph_api.util.log import get_logger

logger = get_logger(__name__)


_RETRIES = 5
_MULTIPLIER = 3


def load_snapshot(tmp_dir):
    """

    :param tmp_dir:
    :return: None
    """
    users_retry = _retry(get_users)
    user_file = users_retry(_RETRIES, _MULTIPLIER,
                            tmp_root=tmp_dir, limit=GRAPH_PAGE_SIZE)

    logger.info(f'Uploading user snapshot to lake.')

    LakeFactory().upload_files(lake_container=LAKE_CONTAINER,
                               lake_dir=LAKE_PATH, files=[user_file])

    logger.info(f'Saving delta link to establish "sync from now".')

    delta_link_retry = _retry(get_delta_link)
    delta_link = delta_link_retry(_RETRIES, _MULTIPLIER)
    delta_link.update({'saved_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')})

    BlobFactory().upload(container=BLOB_CONTAINER, blob_path=BLOB_PATH,
                         source=json.dumps(delta_link, indent=4))


def load_delta(save_point_path, tmp_dir):
    """

    :param save_point_path:
    :param tmp_dir:
    :return: None
    """
    delta_link = load_from_path(save_point_path)

    assert delta_link and '@odata.deltaLink' in delta_link, \
        "Unknown error: delta link not found."

    logger.info(f'Retrieving user delta (ids only) from Graph.')

    delta_list_retry = _retry(get_delta_list)
    delta_link, ids = delta_list_retry(_RETRIES, _MULTIPLIER,
                                       uri=delta_link['@odata.deltaLink'])

    if delta_link and ids:
        logger.info(f'Retrieving user delta from Graph.')

        delta_retry = _retry(get_delta)
        user_file = delta_retry(_RETRIES, _MULTIPLIER,
                                user_list=ids, tmp_root=tmp_dir)

        logger.info(f'Uploading user delta to lake.')

        LakeFactory().upload_files(lake_container=LAKE_CONTAINER,
                                   lake_dir=LAKE_PATH, files=[user_file])

        delta_link.update({'saved_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')})

        BlobFactory().upload(container=BLOB_CONTAINER, blob_path=BLOB_PATH,
                             source=json.dumps(delta_link, indent=4))


def _backoff(multiplier):
    """
    Generate an exponential series.

    :param multiplier:
    :return:
    """
    power = 0

    while True:
        yield multiplier * (2 ** power)
        power += 1


def _retry(method):
    def redo(retries, multiplier, **kwargs):
        """
        Bespoke retry strategy based on existence of "Retry-After".

        :param retries:
        :param multiplier:
        :return:
        """
        delay, delays = 0, _backoff(multiplier)
        cycle = 0

        while cycle < retries:
            try:
                cycle += 1
                return method(**kwargs)

            except RetryableError as e:
                logger.error(f"Retryable: {e}")

                if e.retry_after:
                    logger.debug(f"Retry #{cycle} with delay of {e.retry_after}.")
                    sleep(e.retry_after)
                    delay, delays = 0, _backoff(multiplier)  # reset
                else:
                    delay += next(delays)
                    logger.debug(f"Retry # {cycle} with delay of {delay}.")
                    sleep(delay)

        raise RetryExceededError("Retries exceeded.")

    return redo
