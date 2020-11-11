import json
import logging

from adal import AuthenticationContext
import requests
from requests.exceptions import HTTPError

from client import (
    AUTHORITY, TENANT_ID, CLIENT_ID, CLIENT_KEY, CRM_RESOURCE
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
    oauth_token = oauth.acquire_token_with_client_credentials(CRM_RESOURCE,
                                                              CLIENT_ID,
                                                              CLIENT_KEY)
    return {
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Authorization": f"Bearer {oauth_token['accessToken']}"
    }


def hello_world():
    """
    Basic authorization and simple GET request.

    :param base_url: base URL for request
    :param headers: HTTP request headers
    :return: None
    """
    api_version = '9.1'
    base_url = f"{CRM_RESOURCE}/api/data/v{api_version}"
    url = f"{base_url}/WhoAmI"

    r = requests.get(url, headers=_get_oauth())
    r_payload = r.json()

    logger.info(f"UserId: {r_payload['UserId']}")
    logger.info(f"OrganizationId: {r_payload['OrganizationId']}")


def get_patients(by_filter):
    """
    GET a list of patients.

    Usage:
    ```
    get_patients(by_filter="contains(pah_name, 'Saitama Sensei')")
    ```

    :param by_filter: patient OData filter
    :return: list of Patient dict
    """
    url = f"{CRM_RESOURCE}/api/data/v9.1/pah_patients"

    headers = _get_oauth()
    headers['Prefer'] = 'odata.include-annotations="*"'

    url_params = {
        '$filter': by_filter,
        '$count': 'true'
    }

    try:
        r = requests.get(url, headers=headers, params=url_params)
        r.raise_for_status()
        r_payload = r.json()
    except HTTPError as e:
        logger.error(e)
        raise e

    return_count = r_payload['@odata.count']
    assert return_count > 0, "Patient filter returned no results."

    logger.debug(f"Patient count: {return_count}")

    for patient in r_payload['value']:
        logger.debug(f"pah_patientid: {patient['pah_patientid']}")
        logger.debug(f"pah_name: {patient['pah_name']}")
        logger.debug(f"pah_gender: {patient['pah_gender@OData.Community.Display.V1.FormattedValue']}")
        logger.debug(f"pah_address1_telephone1: {patient['pah_address1_telephone1']}")

    return r_payload['value']


def get_patient(by_filter):
    """
    GET a single patient.

    Usage:
    ```
    get_patient(by_filter="pah_name eq 'Saitama Sensei'")
    ```

    :param by_filter: patient OData filter
    :return: Patient dict
    """
    url = f"{CRM_RESOURCE}/api/data/v9.1/pah_patients"

    headers = _get_oauth()
    headers['Prefer'] = 'odata.include-annotations="*"'

    url_params = {
        '$filter': by_filter,
        '$count': 'true'
    }

    try:
        r = requests.get(url, headers=headers, params=url_params)
        r.raise_for_status()
        r_payload = r.json()
    except HTTPError as e:
        logger.error(e)
        raise e

    return_count = r_payload['@odata.count']
    assert return_count == 1, "Patient filter returned no results."

    patient = r_payload['value'][0]

    logger.debug(f"Patient count: {return_count}")
    logger.debug(f"pah_patientid: {patient['pah_patientid']}")
    logger.debug(f"pah_name: {patient['pah_name']}")
    logger.debug(f"pah_gender: {patient['pah_gender@OData.Community.Display.V1.FormattedValue']}")
    logger.debug(f"pah_address1_telephone1: {patient['pah_address1_telephone1']}")

    return patient


def update_patient(by_filter, data):
    """
    PATCH a patient.

    Usage:
    ```
    payload = {
        "emailaddress": "johnny5@nomail.com",
        "pah_address1_telephone1": "3241112222",
        "pah_address1_line1": f"Address1-{datetime.now().isoformat()}",
        "pah_address1city": f"Marfa-{datetime.now().isoformat()}",
        "pah_address1_stateorprovince": f"Texas",
        "pah_address1_postalcode": f"79757",
        "pah_birthdate": datetime(year=2020, month=5, day=17).isoformat(),
        "pah_gender": "804150000",
    }
    update_patient(by_filter="pah_name eq 'Saitama Sensei'",
                   data=payload)
    ```

    :param by_filter: patient OData filter
    :param data: patient key/value pairs
    :return: Patient dict
    """
    base_url = f"{CRM_RESOURCE}/api/data/v9.1"

    headers = _get_oauth()
    patient = get_patient(base_url, headers, by_filter)

    headers.update({
        "Content-Type": "application/json",
        'Prefer': 'return=representation'
    })
    url = f"{base_url}/pah_patients({patient['pah_patientid']})"

    try:
        r = requests.patch(url, headers=headers, data=json.dumps(data))
        r.raise_for_status()
        patient = r.json()
    except HTTPError as e:
        logger.error(e)
        raise e

    logger.debug(f"pah_patientid: {patient['pah_patientid']}")
    logger.debug(f"pah_name: {patient['pah_name']}")
    logger.debug(f"pah_address1_line1: {patient['pah_address1_line1']}")
    logger.debug(f"pah_address1_telephone1: {patient['pah_address1_telephone1']}")
    logger.debug(f"pah_birthdate: {patient['pah_birthdate']}")
    logger.debug(f"emailaddress: {patient['emailaddress']}")

    return patient


def create_patient(data):
    """
    POST a patient.

    Usage:
    ```
    payload = {
        "pah_name": "Saitama Sensei2",
        "emailaddress": "johnny5@mail7.com",
        "pah_address1_telephone1": "3241112222",
        "pah_birthdate": datetime(year=2020, month=5, day=17).isoformat(),
        "pah_gender": "804150000",
    }
    create_patient(data=payload)
    ```

    :param data: patient key/value pairs
    :return: Patient dict
    """
    url = f"{CRM_RESOURCE}/api/data/v9.1/pah_patients"

    headers = _get_oauth()
    headers.update({
        "Content-Type": "application/json",
        'Prefer': 'return=representation'
    })

    try:
        r = requests.post(url, headers=headers, data=json.dumps(data))
        r.raise_for_status()
        patient = r.json()
    except HTTPError as e:
        logger.error(e)
        raise e

    logger.debug(f"pah_patientid: {patient['pah_patientid']}")
    logger.debug(f"pah_name: {patient['pah_name']}")
    logger.debug(f"pah_address1_telephone1: {patient['pah_address1_telephone1']}")
    logger.debug(f"pah_birthdate: {patient['pah_birthdate']}")
    logger.debug(f"emailaddress: {patient['emailaddress']}")

    return patient


def delete_patient(by_filter):
    """
    DELETE a patient.

    Usage:
    ```
    delete_patient(by_filter="pah_name eq 'Saitama Sensei2'")
    ```
    :param by_filter: patient OData filter
    :return: None
    """
    base_url = f"{CRM_RESOURCE}/api/data/v9.1"
    headers = _get_oauth()

    patient = get_patient(base_url, headers, by_filter)

    # headers.update({
    #     "Content-Type": "application/json"
    # })
    url = f"{base_url}/pah_patients({patient['pah_patientid']})"

    try:
        r = requests.delete(url, headers=headers)
        r.raise_for_status()
    except HTTPError as e:
        logger.error(e)
        raise e
