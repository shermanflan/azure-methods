"""
Inspired by
[Azure Samples](https://github.com/Azure-Samples/aci-docs-sample-python/blob/master/src/aci_docs_sample.py)
"""
import json
import logging
from os import getenv
import time

from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (
    ContainerGroup, ImageRegistryCredential, Container,
    EnvironmentVariable, ResourceRequirements, ResourceRequests,
)
from msrestazure.azure_exceptions import CloudError
import yaml

logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s]: %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger('msrest').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('adal-python').setLevel(logging.ERROR)


def custom_poller(aci_poller, client, resource, name):
    """
    Custom polling loop for ACI creation and destruction.

    :param aci_poller: AzureOperationPoller
    :param client: ContainerInstanceManagementClient
    :param resource: Azure resource group
    :param name: Azure ACI name
    :return: None
    """
    max_wait = 100

    while True and max_wait > 0:

        logger.info(f'ACI creation status: {aci_poller.status()}')
        logger.info(f'ACI creation done: {aci_poller.done()}')

        time.sleep(30)

        if aci_poller.done():

            logger.info(f'ACI creation status: {aci_poller.status()}')
            logger.info(f'ACI creation done: {aci_poller.done()}')

            inspect = client.container_groups.get(resource_group_name=resource,
                                                  container_group_name=name,
                                                  raw=False)

            logger.info(f'ACI provisioning state: {inspect.provisioning_state}')

            if aci_poller.done() \
                    and aci_poller.status() == 'Succeeded' \
                    and inspect.provisioning_state == 'Succeeded':

                time.sleep(30)

                logger.info(f'Deleting ACI')

                client.container_groups.delete(
                    resource_group_name=resource,
                    container_group_name=name
                )

                break
            else:
                raise Exception("Invalid ACI provisioning state")

        max_wait -= 1


if __name__ == '__main__':

    auth_path = getenv('AZURE_AUTH_LOCATION',
                       '/home/condesa1931/personal/github/azure-methods/ManageACI/scripts/acioperator.auth.json')
    yaml_path = getenv('ACI_DEFINITION',
                       '/home/condesa1931/personal/github/azure-methods/ManageACI/scripts/box2lake-dev.yml')
    rg = getenv('AZURE_RESOURCE_GROUP', 'ACIResourceGroup')

    # TODO: Use RBAC for registry authentication
    # https://docs.microsoft.com/en-us/azure/container-registry/container-registry-auth-aci

    # Authenticate the management clients with Azure.
    # Set AZURE_AUTH_LOCATION to the path to an auth file.
    # Usage: az ad sp create-for-rbac --sdk-auth > my.azureauth
    if auth_path is not None:

        logger.info(f"Authenticating with credentials file {auth_path}")

        aci_client = get_client_from_auth_file(
            ContainerInstanceManagementClient,
            auth_path=auth_path
        )
    else:
        raise Exception("Authentication failure")

    with open(yaml_path, 'r') as f:
        try:
            aci_config = yaml.safe_load(f)
            aci_config['apiVersion'] = aci_config['apiVersion'].strftime('%Y-%m-%d')
        except yaml.YAMLError as e:
            raise e

    logger.info('Defining container group')

    containers = []

    for c in aci_config['properties']['containers']:

        config = [EnvironmentVariable(name=p['name'],
                                      value=p.get('value'),
                                      secure_value=p.get('secureValue'))
                  for p in c['properties']['environmentVariables']]

        resources = ResourceRequests(
            cpu=c['properties']['resources']['requests']['cpu'],
            memory_in_gb=c['properties']['resources']['requests']['memoryInGB']
        )

        unit = Container(name=c['name'],
                         image=c['properties']['image'],
                         resources=ResourceRequirements(
                             requests=resources,
                             limits=None,  # ResourceLimits()
                         ),
                         environment_variables=config)

        containers.append(unit)

    registries = [ImageRegistryCredential(**p)
                  for p in aci_config['properties']['imageRegistryCredentials']]

    group = ContainerGroup(containers=containers,
                           os_type=aci_config['properties']['osType'],
                           location=aci_config['location'],
                           image_registry_credentials=registries,
                           restart_policy=aci_config['properties']['restartPolicy'])

    logger.info('Creating container group')

    try:
        poller = aci_client.container_groups.create_or_update(
            resource_group_name=rg,
            container_group_name=aci_config['name'],
            container_group=group
        )
    except CloudError as e:
        raise e

    logger.info('Polling container group creation')

    def handler(operation):

        logger.debug(f'Callback status(): {operation.status()}')
        logger.debug(f'Callback finished(): {operation.finished()}')

        if operation.finished() and operation.status() == 'Succeeded':

            time.sleep(30)

            logger.info(f'Deleting ACI')

            aci_client.container_groups.delete(
                resource_group_name=rg,
                container_group_name=aci_config['name']
            )
        else:
            raise Exception("Invalid provisioning state")

    poller.add_done_callback(handler)
    poller.wait()

    # Alternatively, run a manual poller.
    # custom_poller(aci_poller=poller, client=aci_client, resource=rg,
    #               name=aci_config['name'])

    logger.info('Process complete')