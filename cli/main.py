import logging
import json
import os

import click
from pyfiglet import Figlet

from utility import DIAGNOSTIC_NAME
from utility.cmd import (get_by_tag, add_diagnostics,
                         remove_diagnostics, is_monitored)
from utility import log

logger = logging.getLogger(__name__)

fig = Figlet(font='speed')
banner = '\b' + os.linesep + \
         fig.renderText("BSH Enterprise Analytics")


@click.group(help=banner)
def cli():
    pass


@cli.command()
@click.option('--subscription', required=True,
              help='The Azure subscription name or id.')
@click.option('--tag_name', required=True,
              default='auto-monitor', show_default=True,
              help='The resource tag.')
@click.option('--tag_value', required=True,
              default='True', show_default=True,
              help='The resource tag value: True or False.')
@click.option('--resource_group', required=False,
              help='The resource group.')
@click.option('--resource_type', required=False,
              help='The resource category.')
def show(subscription, tag_name, tag_value, resource_group=None,
         resource_type=None):
    """
    Show resource diagnostic settings.

    \b
    :param subscription: The subscription id
    :param tag_name: Refers to the preconfigured resource tag
    :param tag_value: Refers to the preconfigured resource tag value
    :param resource_group: The resource group
    :param resource_type: The resource type
    :return: list of resource ids.
    """
    rids = get_by_tag(subscription, tag_name, tag_value,
                      resource_group, resource_type)

    message = {
        os.path.split(rid)[1]: {
            "Type": c,
            DIAGNOSTIC_NAME: is_monitored(DIAGNOSTIC_NAME, rid)
        }
        for rid, c in rids
    }

    click.echo(json.dumps(message, indent=4))


@cli.command()
@click.option('--name', required=True,
              help='The diagnostic setting name.')
@click.option('--subscription', required=True,
              help='The Azure subscription name or id.')
@click.option('--workspace_id', required=True,
              help='The Azure Log Analytics workspace id.')
@click.option('--tag_name', required=True,
              default='auto-monitor', show_default=True,
              help='The resource tag.')
@click.option('--tag_value', required=True, default='True',
              help='The resource tag value: True or False.')
def add(name, subscription, workspace_id, tag_name, tag_value):
    """
    Configure resource diagnostic settings.

    \b
    :param name: The diagnostic setting name
    :param subscription: The Azure subscription id
    :param workspace_id: The Log Analytics workspace id
    :param tag_name: The specified resource tag name
    :param tag_value: The specified resource tag value
    :return: None
    """
    add_diagnostics(name, subscription, workspace_id,
                    tag_name, tag_value)


@cli.command()
@click.option('--name', required=True,
              help='The diagnostic setting name.')
@click.option('--subscription', required=True,
              help='The Azure subscription name or id.')
@click.option('--tag_name', required=True,
              default='auto-monitor', help='The resource tag.')
@click.option('--tag_value', required=True,
              default='True', show_default=True,
              help='The resource tag value: True or False.')
def remove(name, subscription, tag_name, tag_value):
    """
    Removes resource diagnostic settings.

    \b
    :param name: The diagnostic setting name
    :param subscription: The Azure subscription id
    :param tag_name: The specified resource tag name
    :param tag_value: The specified resource tag value
    :return: None
    """
    resources = get_by_tag(subscription, tag_name, tag_value)

    if click.confirm(f'{len(resources)} diagnostic settings will be' +
                     ' removed. Would you like to proceed?'):
        remove_diagnostics(name, subscription, tag_name, tag_value)


if __name__ == '__main__':

    cli()

