from datetime import datetime
import json
import os

from adal import AuthenticationContext
import pyodbc
import requests
from requests.exceptions import HTTPError

from python_client.util.log_config import root_logger as logger


def hello_world(base_url, headers):
    """
    Basic authorization and simple GET request.

    :param base_url: base URL for request
    :param headers: HTTP request headers
    :return: None
    """
    url = f"{base_url}/WhoAmI"

    r = requests.get(url, headers=headers)
    r_payload = r.json()

    logger.info(f"UserId: {r_payload['UserId']}")
    logger.info(f"OrganizationId: {r_payload['OrganizationId']}")


def get_patients(base_url, headers, by_filter):
    """
    GET a list of patients.

    :param base_url: base URL for request
    :param headers: HTTP request headers
    :param by_filter: patient OData filter
    :return: list of Patient dict
    """
    headers['Prefer'] = 'odata.include-annotations="*"'
    url_params = {
        '$filter': by_filter,
        '$count': 'true'
    }
    url = f"{base_url}/pah_patients"

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


def get_patient(base_url, headers, by_filter):
    """
    GET a single patient.

    :param base_url: base URL for request
    :param headers: HTTP request headers
    :param by_filter: patient OData filter
    :return: Patient dict
    """
    headers['Prefer'] = 'odata.include-annotations="*"'
    url_params = {
        '$filter': by_filter,
        '$count': 'true'
    }
    url = f"{base_url}/pah_patients"

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


def update_patient(base_url, headers, by_filter, data):
    """
    PATCH a patient.

    :param base_url: base URL for request
    :param headers: HTTP request headers
    :param by_filter: patient OData filter
    :param data: patient key/value pairs
    :return: Patient dict
    """
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


def create_patient(base_url, headers, data):
    """
    POST a patient.

    :param base_url: base URL for request
    :param headers: HTTP request headers
    :param data: patient key/value pairs
    :return: Patient dict
    """
    headers.update({
        "Content-Type": "application/json",
        'Prefer': 'return=representation'
    })
    url = f"{base_url}/pah_patients"

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


def delete_patient(base_url, headers, by_filter):
    """
    DELETE a patient.

    :param base_url: base URL for request
    :param headers: HTTP request headers
    :param by_filter: patient OData filter
    :return: None
    """
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


def hello_odbc(cnxn_str):
    """
    Simple connection via ODBC.

    :param cnxn_str: the full connection string
    :return: None
    """

    # This calls cnxn.commit() when going out of scope.
    with pyodbc.connect(cnxn_str, autocommit=False) as cnxn:
        cursor = cnxn.cursor()
        qry1 = """
            SELECT  source
                    , [Pharmacy Code] AS PharmacyCode
                    , patientKey
            FROM    [dbo].[patientFinPlan] WITH (READUNCOMMITTED)
            ORDER BY [CHANGE DATE]
            OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY;
        """

        # Iterate through result set, row by row
        for row in cursor.execute(qry1):
            logger.info(f"DB TEST: {row.source}, {row.PharmacyCode}, {row.patientKey}")


# TODO: Create a .NET core:Ubuntu image?
if __name__ == "__main__":

    authority = 'https://login.microsoftonline.com'  # TODO: move to env var
    tenant_id = os.environ['AAD_TENANT']
    client_id = os.environ['AAD_CLIENT']
    client_secret = os.environ['AAD_SECRET']
    base_resource = os.environ['AAD_RESOURCE']
    driver = os.environ['DB_DRIVER']
    server = os.environ['DB_SERVER']
    database = os.environ['DB']
    username = os.environ['DB_USER']
    password = os.environ['DB_PWD']

    cnxn_str = 'DRIVER={0};SERVER={1};DATABASE={2};UID={3};PWD={4}'.format(
        driver, server, database, username, password
    )

    hello_odbc(cnxn_str)

    api_version = '9.1'
    request_url = f"{base_resource}/api/data/v{api_version}"

    oauth = AuthenticationContext(authority=f'{authority}/{tenant_id}')
    oauth_token = oauth.acquire_token_with_client_credentials(base_resource,
                                                              client_id,
                                                              client_secret)
    common_headers = {
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Authorization": f"Bearer {oauth_token['accessToken']}"
    }

    # API access example
    # hello_world(base_url=request_url, headers=common_headers)

    # GET pah_patient
    # get_patients(base_url=request_url, headers=common_headers,
    #              by_filter="contains(pah_name, 'Saitama Sensei')")

    # get_patient(base_url=request_url, headers=common_headers,
    #             by_filter="pah_name eq 'Saitama Sensei'")

    # PATCH pah_patient
    # payload = {
    #     "emailaddress": "johnny5@nomail.com",
    #     "pah_address1_telephone1": "3241112222",
    #     "pah_address1_line1": f"Address1-{datetime.now().isoformat()}",
    #     "pah_address1city": f"Marfa-{datetime.now().isoformat()}",
    #     "pah_address1_stateorprovince": f"Texas",
    #     "pah_address1_postalcode": f"79757",
    #     "pah_birthdate": datetime(year=2020, month=5, day=17).isoformat(),
    #     "pah_gender": "804150000",
    # }
    # update_patient(base_url=request_url, headers=common_headers,
    #                by_filter="pah_name eq 'Saitama Sensei'",
    #                data=payload)

    # POST pah_patient
    # payload = {
    #     "pah_name": "Saitama Sensei2",
    #     "emailaddress": "johnny5@mail7.com",
    #     "pah_address1_telephone1": "3241112222",
    #     "pah_birthdate": datetime(year=2020, month=5, day=17).isoformat(),
    #     "pah_gender": "804150000",
    # }
    # create_patient(base_url=request_url, headers=common_headers,
    #                data=payload)

    # DELETE pah_patient
    # delete_patient(base_url=request_url, headers=common_headers,
    #                by_filter="pah_name eq 'Saitama Sensei2'")

    logger.info(f"Processing complete...")
