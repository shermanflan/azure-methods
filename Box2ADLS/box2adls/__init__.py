from datetime import date
from os import environ
from os.path import join

from box2adls.util import get_last_friday


_year = date.today().strftime("%Y")
_month_folder = date.today().strftime("%m-%B")
_day_suffix = date.today().strftime("%m_%d_%Y")
_day_suffix2 = get_last_friday(date.today()).strftime("%m.%d.%Y")

BOX_USER = environ.get('BOX_USER_ID', '')
BOX_FOLDER = environ.get('BOX_FOLDER_ID', '')
BOX_PATH = join(environ.get('BOX_FOLDER_PATH',
                            'Utilization Reports/Daily Schedule Status Reports/{0} Reports').format(_year),
                f"{_month_folder}")
BOX_PATH2 = join(environ.get('BOX_FOLDER_PATH2',
                             'Utilization Reports/Weekly Utilization Reports/{0} Reports').format(_year),
                 f"{_month_folder}")
BOX_MASK = environ.get('BOX_FILE_MASK',
                       'Branch Scheduled Hours Breakdown_{0}.xlsx').format(_day_suffix)
BOX_MASK2 = environ.get('BOX_FILE_MASK2',
                        'Telephony Usage By Branch {0}.xlsx').format(_day_suffix2)
BOX_RENAME = environ.get('BOX_FILE_RENAME', 'Branch Scheduled Hours Breakdown.xlsx')
TAB_NAME_PREV = environ.get('WS_PREV_NAME', 'PreviousMonth')
TAB_NAME_CURR = environ.get('WS_CURR_NAME', 'CurrentMonth')
TAB_NAME_NEXT = environ.get('WS_NEXT_NAME', 'NextMonth')
BOX_RENAME2 = environ.get('BOX_FILE_RENAME2', 'Telephony Usage By Branch.xlsx')
TAB_HIDDEN_NAME = environ.get('WS_HIDDEN_NAME', '{0} Tele Stats').format(_year)
TAB_HIDDEN_RENAME = environ.get('WS_HIDDEN_RENAME', 'Tele Stats')

LAKE_ACCOUNT = environ.get('LAKE_ACCOUNT_NAME', '')
LAKE_KEY = environ.get('LAKE_ACCOUNT_KEY',
                       '')
LAKE_URL = f'https://{LAKE_ACCOUNT}.dfs.core.windows.net/'
LAKE_CONTAINER = environ.get('LAKE_CONTAINER_NAME', 'enterprisedata')
LAKE_PATH = environ.get('LAKE_FOLDER_PATH', 'Raw/BOX Reports')
