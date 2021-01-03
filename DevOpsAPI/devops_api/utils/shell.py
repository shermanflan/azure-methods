import logging
from subprocess import run, CalledProcessError

from devops_api.utils import log

logger = logging.getLogger(__name__)


def run_cmd(cmd):
    try:
        result = run(cmd, shell=False, capture_output=True, check=True,
                     encoding="utf-8", text=True)

        return result
    except CalledProcessError as e:

        logger.exception(e)

        raise