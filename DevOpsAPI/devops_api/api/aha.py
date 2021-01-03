import logging

import requests
from requests.exceptions import HTTPError

from devops_api import (
    AHA_ENDPOINT, AHA_APP_KEY,
)
from devops_api.utils import log
from devops_api.utils.error import RetryableError
from devops_api.utils.shell import run_cmd

logger = logging.getLogger(__name__)


def get_account_backup(backup_id, out_directory):
    """

    :param backup_id:
    :type backup_id: String
    :param out_directory:
    :type out_directory: String
    :return: path to account_backup as String
    """
    with requests.Session() as session:
        try:
            resource = "account_backups"
            backup_uri = f"{AHA_ENDPOINT}/{resource}/{backup_id}.tgz"
            headers = {
                "Authorization": f"Bearer {AHA_APP_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            r = session.get(backup_uri, headers=headers, stream=True)
            r.raise_for_status()

            save_path = f"{out_directory}/{backup_id}.tgz"

            with open(save_path, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=512):
                    fd.write(chunk)

            cmd = [
                'tar', '--extract',
                '-vf', save_path,
                f"--one-top-level={out_directory}"
            ]
            extract_filename = run_cmd(cmd).stdout.rstrip()

            return f"{out_directory}/{extract_filename}"
        except HTTPError as e:

            # logger.error(f'Request error', status_code=r.status_code, source=backup_uri)
            logger.exception(e)

            if e.response.status_code in (429, 503, 504):
                logger.error('Server overloaded')
                raise RetryableError('Retrying account backup download')

            raise
