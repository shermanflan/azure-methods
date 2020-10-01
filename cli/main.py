import json
import logging
from os import linesep
from subprocess import run, CalledProcessError

from utility import AZ_SUBSCRIPTION, AZ_RESOURCE_GROUP
from utility import log

logger = logging.getLogger(__name__)

# TODO: Add CLI support
# TODO: Run az login for delegated auth?
if __name__ == '__main__':

    factory_cmd = [
        'az', 'resource', 'list',
        '--resource-type', 'Microsoft.DataFactory/factories',
        '--resource-group', AZ_RESOURCE_GROUP,
        '--subscription', AZ_SUBSCRIPTION
    ]

    try:
        result = run(factory_cmd, shell=False,
                     capture_output=True, check=True,
                     encoding="utf-8", text=True)

        trimmed = result.stdout[:result.stdout.rfind(']') + 1]
        adf_map = json.loads(trimmed)
        adf_names = [f['name'] for f in adf_map]

        logger.debug(result.stdout)
        logger.debug(f'Total: {len(adf_names)}')
        logger.debug(linesep.join(adf_names))

    except CalledProcessError as e:

        logger.exception(e)
        raise
