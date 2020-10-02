from os import environ

APP_LOG_KEY = environ.get('APP_LOG_KEY', 'bhs.aci.graph2lake.dev')
_AAD_TENANT_ID = environ.get('AAD_TENANT_ID', '')
AAD_ENDPOINT = f'https://login.microsoftonline.com/{_AAD_TENANT_ID}'
APP_ID = environ.get('APP_ID', '')
APP_SECRET = environ.get('APP_SECRET', '')
APP_INSIGHTS_KEY = environ.get('APP_INSIGHTS_KEY', '')

GRAPH_API_SCOPES = environ.get('GRAPH_API_SCOPES', 'https://graph.microsoft.com/.default').split(',')
GRAPH_API_ENDPOINT = environ.get('GRAPH_API_ENDPOINT', 'https://graph.microsoft.com/v1.0')
GRAPH_META = environ.get('GRAPH_META', 'id,displayName,givenName,surname,userPrincipalName,' +
                         'jobTitle,companyName,department,officeLocation,' +
                         'employeeId,mail,onPremisesDomainName,createdDateTime')
GRAPH_PAGE_SIZE = environ.get('GRAPH_PAGE_SIZE', '250')

_STORE_ACCOUNT = environ.get('STORE_ACCOUNT_NAME', '')
STORE_KEY = environ.get('STORE_ACCOUNT_KEY', '')

BLOB_URL = f'https://{_STORE_ACCOUNT}.blob.core.windows.net/'
BLOB_CONTAINER = environ.get('BLOB_CONTAINER_NAME', 'python-app-data')
BLOB_PATH = environ.get('BLOB_PATH', 'graph-api/next_delta.json')

LAKE_URL = f'https://{_STORE_ACCOUNT}.dfs.core.windows.net/'
LAKE_CONTAINER = environ.get('LAKE_CONTAINER_NAME', 'enterprisedata')
LAKE_PATH = environ.get('LAKE_FOLDER_PATH', 'Raw/Graph Deltas')