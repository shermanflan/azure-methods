import logging

from adal import AuthenticationContext
import requests
from requests.exceptions import HTTPError

from client import (
    AUTHORITY, TENANT_ID, CLIENT_ID, CLIENT_KEY,
    CI_RESOURCE, CI_API_RESOURCE, CI_INSTANCE_ID
)
import client.util.log_config

logger = logging.getLogger(__name__)


def _get_oauth():
    """
    TODO:
    - Cache the context and token.

    :return: Dictionary of headers including bearer token
    """
    oauth = AuthenticationContext(authority=f'{AUTHORITY}/{TENANT_ID}')
    oauth_token = oauth.acquire_token_with_client_credentials(CI_RESOURCE,
                                                              CLIENT_ID,
                                                              CLIENT_KEY)
    return {
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Authorization": f"Bearer {oauth_token['accessToken']}"
    }


def get_instances():
    """
    GET a list of Customer Insights instances.

    :return: list of Instances dict
    """
    url = f"{CI_API_RESOURCE}/api/instances"

    headers = _get_oauth()
    headers['Prefer'] = 'odata.include-annotations="*"'

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r_payload = r.json()
    except HTTPError as e:
        logger.error(e)
        raise e

    return_count = len(r_payload)
    assert return_count > 0, "Instances request returned no results."

    logger.debug(f"Instances count: {return_count}")

    for i in r_payload:
        logger.debug(f"instanceId: {i['instanceId']}")
        logger.debug(f"name: {i['name']}")
        logger.debug(f"scaleUnitUri: {i['scaleUnitUri']}")
        logger.debug(f"instanceType: {i['instanceType']}")

    return r_payload


def get_entity(name):
    """
    GET a single patient.

    Usage:
    ```
    get_entity(name="Customer")
    ```

    :param by_filter: patient OData filter
    :return: Patient dict
    """
    url = f"{CI_API_RESOURCE}/api/instances/{CI_INSTANCE_ID}/manage/entities/{name}"

    headers = _get_oauth()
    headers['Prefer'] = 'odata.include-annotations="*"'

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r_payload = r.json()
    except HTTPError as e:
        logger.error(e)
        raise e

    return_count = len(r_payload)
    assert return_count > 0, f"Entity request for {name} returned no results."

    entity = r_payload

    logger.debug(f"Entity: {entity['name']}")
    logger.debug(f"Qualified Name: {entity['qualifiedEntityName']}")
    logger.debug(f"Data Source: {entity['dataSourceName']}")
    logger.debug(f"Type: {entity['entityType']}")
    logger.debug(f"Attribute Count: {len(entity['attributes'])}")

    return entity
