import os

from adal import AuthenticationContext
import requests


def hello_world(resource, token):
    """
    Basic authorization and simple GET request.
    :return: None
    """
    headers = {
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Authorization": f"Bearer {token}"
    }

    url = f"{resource}/WhoAmI"

    r = requests.get(url, headers=headers)
    r_payload = r.json()
    print(f"UserId: {r_payload['UserId']}")
    print(f"OrganizationId: {r_payload['OrganizationId']}")


if __name__ == "__main__":

    tenant_id = os.environ['AAD_TENANT']
    client_id = os.environ['AAD_CLIENT']
    client_secret = os.environ['AAD_SECRET']
    base_url = os.environ['AAD_RESOURCE']

    auth_context = AuthenticationContext(authority=f'https://login.microsoftonline.com/{tenant_id}')
    oauth_token = auth_context.acquire_token_with_client_credentials(base_url, client_id, client_secret)

    api_version = '9.1'
    hello_world(resource=f"{base_url}/api/data/v{api_version}/", token=oauth_token['accessToken'])

    print(f"Processing complete...")
