import logging
import json
import os
from subprocess import run, CalledProcessError

import click

from utility import LOG_MAP, METRIC_MAP
from utility import log

logger = logging.getLogger(__name__)


def get_by_tag(subscription, tag_name, tag_value,
               resource_group=None, resource_type=None):
    """
    Get resources by tag. Each resource should have a tag named
    'auto-monitor' in order to be configured for automation.

    :param subscription: The subscription id
    :param tag_name: Refers to the preconfigured resource tag
    :param tag_value: Refers to the preconfigured resource tag value
    :param resource_group: The resource group
    :param resource_type: The resource type
    :return: list of resource ids.
    """
    az_cmd = [
        'az', 'resource', 'list',
        '--subscription', subscription,
    ]

    if resource_group:
        az_cmd.extend(['--resource-group', resource_group])

    if resource_type:
        az_cmd.extend(['--resource-type', resource_type])

    try:
        result = run(az_cmd, shell=False, capture_output=True, check=True,
                     encoding="utf-8", text=True)

        end_brace = max(result.stdout.rfind(']'), result.stdout.rfind('}'))
        trimmed = result.stdout[:end_brace+1]
        resources = json.loads(trimmed)
        resource_ids = []

        for f in resources:
            if f['tags'] and tag_name in f['tags'] \
                    and tag_value == f['tags'][tag_name]:
                resource_ids.append((f['id'], f['type']))

        return resource_ids
    except CalledProcessError as e:

        logger.exception(e)

        raise


def add_diagnostics(name, subscription, workspace_id, tag_name,
                    tag_value):
    """
    Adds the specified diagnostic setting to all resources with the
    specified tag/value pair.

    :param name: The diagnostic setting name
    :param subscription: The Azure subscription id
    :param workspace_id: The Log Analytics workspace id
    :param tag_name: The specified resource tag name
    :param tag_value: The specified resource tag value
    :return: None
    """
    resources = get_by_tag(subscription, tag_name, tag_value)

    click.echo(f'Found {len(resources)} resources.')

    for rid, category in resources:
        if not is_monitored(name, rid):
            add_diagnostic(name, rid, category, workspace_id)


def remove_diagnostics(name, subscription, tag_name, tag_value):
    """
    Removes the specified diagnostic setting from all resources with the
    specified tag/value pair.

    :param name: The diagnostic setting name
    :param subscription: The Azure subscription id
    :param tag_name: The specified resource tag name
    :param tag_value: The specified resource tag value
    :return: None
    """
    resources = get_by_tag(subscription, tag_name, tag_value)

    click.echo(f'Found {len(resources)} resources.')

    for rid, category in resources:
        if is_monitored(name, rid):
            remove_diagnostic(name, rid)


def has_diagnostics(resource_id):
    """
    Check if resource_id has at least one diagnostic setting.

    :param resource_id: The resource id
    :return: True or False
    """
    az_cmd = [
        'az', 'monitor', 'diagnostic-settings', 'list',
        '--resource', resource_id,
    ]

    try:
        result = run(az_cmd, shell=False, capture_output=True, check=True,
                     encoding="utf-8", text=True)

        end_brace = max(result.stdout.rfind(']'), result.stdout.rfind('}'))
        trimmed = result.stdout[:end_brace+1]
        resource = json.loads(trimmed)

        return True if resource['value'] else False

    except CalledProcessError as e:

        logger.exception(e)
        raise


def is_monitored(name, resource_id):
    """
    Check if resource_id has the specified diagnostic setting.

    :param name: the name of the diagnostic setting
    :param resource_id: the resource id
    :return: True or False
    """
    az_cmd = [
        'az', 'monitor', 'diagnostic-settings', 'show',
        '--name', name,
        '--resource', resource_id,
    ]

    try:
        resource = os.path.split(resource_id)[1]
        result = run(az_cmd, shell=False, capture_output=True, check=True,
                     encoding="utf-8", text=True)

        end_brace = max(result.stdout.rfind(']'), result.stdout.rfind('}'))
        trimmed = result.stdout[:end_brace+1]
        resource = json.loads(trimmed)

        return True if resource['name'] else False

    except CalledProcessError as e:

        click.echo(f'Diagnostic [{name}] does not exist for [{resource}].')
        return False


def remove_diagnostic(name, resource_id):
    """
    Remove the diagnostic setting from the specified resource.

    :param name: The diagnostic setting name
    :param resource_id: The resource id
    :return: None
    """
    try:
        az_cmd = [
            'az', 'monitor', 'diagnostic-settings', 'delete',
            '--name', name,
            '--resource', resource_id
        ]

        logger.debug(az_cmd)

        run(az_cmd, check=True)

        click.echo(f'Removed {name} from {os.path.split(resource_id)[1]}.')

    except CalledProcessError as e:

        logger.exception(e)
        raise


def add_diagnostic(name, resource_id, category, workspace_id,
                   log_map=LOG_MAP, metric_map=METRIC_MAP):
    """
    Adds the diagnostic setting to the specified resource.

    :param name: The diagnostic setting name
    :param resource_id: The resource id
    :param category: The resource type
    :param workspace_id: The log analytics workspace id
    :param log_map: Mapping between resource type and log
    configuration
    :param metric_map: Mapping between resource type and
    metric configuration
    :return: None
    """
    az_cmd = [
        'az', 'monitor', 'diagnostic-settings', 'create',
        '--name', name,
        '--resource', resource_id,
        '--logs', f"{log_map[category]}",
        '--metrics', f"{metric_map[category]}",
        '--workspace', workspace_id,
    ]

    if category == 'Microsoft.DataFactory/factories':
        az_cmd.extend(['--export-to-resource-specific', 'true'])

    logger.debug(az_cmd)

    try:
        run(az_cmd, check=True)

        click.echo(f'Added {name} to {os.path.split(resource_id)[1]}.')

    except CalledProcessError as e:

        logger.exception(e)
        raise
