import json
import logging
from os import linesep
from subprocess import run, CalledProcessError

from utility import (AZ_SUBSCRIPTION, AZ_RESOURCE_GROUP,
                     DIAGNOSTIC_NAME, AZ_LOG_WORKSPACE)
from utility.cmd import add_diagnostic, get_by_tag, is_monitored
from utility import log

logger = logging.getLogger(__name__)

# TODO: Add CLI support
# TODO: Run az login for delegated auth?
if __name__ == '__main__':

    resources = get_by_tag(subscription=AZ_SUBSCRIPTION,
                           resource_group=AZ_RESOURCE_GROUP,
                           tag_name='auto-monitor')

    filtered = [rid for rid, _ in resources if is_monitored(rid)]
