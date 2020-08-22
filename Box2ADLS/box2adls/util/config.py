from datetime import date
from os import environ
from os.path import join


_month_folder = date.today().strftime('%m-%B')
_day_suffix = date.today().strftime('%m_%d_%Y')

BOX_USER = environ.get('BOX_USER_ID', '')
BOX_FOLDER = environ.get('BOX_FOLDER_ID', '')
BOX_PATH = join(environ.get('BOX_FOLDER_PATH',
                            'Utilization Reports/Daily Schedule Status Reports/2020 Reports'),
                f"{_month_folder}")
BOX_MASK = environ.get('BOX_FILE_MASK',
                       'Branch Scheduled Hours Breakdown_{0}.xlsx').format(_day_suffix)
BOX_RENAME = environ.get('BOX_FILE_RENAME', 'Branch Scheduled Hours Breakdown.xlsx')

LAKE_ACCOUNT = environ.get('LAKE_ACCOUNT_NAME', 'pahintegrationstorage')
LAKE_KEY = environ.get('LAKE_ACCOUNT_KEY',
                       '')
LAKE_URL = f'https://{LAKE_ACCOUNT}.dfs.core.windows.net/'
LAKE_CONTAINER = environ.get('LAKE_CONTAINER_NAME', 'enterprisedata')
LAKE_PATH = environ.get('LAKE_FOLDER_PATH', 'Raw/BOX Reports')
