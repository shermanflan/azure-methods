from datetime import datetime, date
from os import environ
from os.path import join
import re

from box2adls.exceptions import FolderMissingError
from box2adls.util import get_last_friday


# _month_folder = date.today().strftime("%m-%B")
# _day_suffix = date.today().strftime("%m_%d_%Y")
# _day_suffix2 = get_last_friday(date.today()).strftime("%m.%d.%Y")
SIMMER = True if environ.get('SIMMER', 'True') == 'True' else False
BROKER_URL = environ.get('BROKER_URL', 'redis://localhost:6379/0')

BOX_CONFIG = environ.get('BOX_CONFIG', 'config/my_config.json')
BOX_USER = environ.get('BOX_USER_ID', '')
BOX_FOLDER = environ.get('BOX_FOLDER_ID', '')
BOX_PATH = join(environ.get('BOX_FOLDER_PATH',
                            'Utilization Reports/Daily Schedule Status Reports/2020 Reports/08-August'))
BOX_PATH2 = join(environ.get('BOX_FOLDER_PATH2',
                             'Utilization Reports/Weekly Utilization Reports/2020 Reports/08-August/August - 21'))
BOX_MASK = environ.get('BOX_FILE_MASK',
                       'Branch Scheduled Hours Breakdown_08_25_2020.xlsx')
BOX_MASK2 = environ.get('BOX_FILE_MASK2',
                        'Telephony Usage By Branch 08.21.2020.xlsx')
BOX_RENAME = environ.get('BOX_FILE_RENAME', 'Branch Scheduled Hours Breakdown.xlsx')
TAB_NAME_PREV = environ.get('WS_PREV_NAME', 'PriorMonth')
TAB_NAME_CURR = environ.get('WS_CURR_NAME', 'CurrentMonth')
TAB_NAME_NEXT = environ.get('WS_NEXT_NAME', 'NextMonth')
BOX_RENAME2 = environ.get('BOX_FILE_RENAME2', 'Telephony Usage By Branch.xlsx')

_re_year = r'.+/(\d\d\d\d) Reports/.+'
_year_match = re.match(_re_year, BOX_PATH, flags=re.I)
_re_day = r'.+(\d\d.\d\d.\d\d\d\d).xlsx$'
_day_match = re.match(_re_day, BOX_MASK, flags=re.I)

if _year_match:
    _year = _year_match.group(1)
else:
    _year = date.today().strftime("%Y")

if _day_match:
    _day = _day_match.group(1)
    RELATIVE_DATE = datetime.strptime(f'{_day}', "%m_%d_%Y")
else:
    raise FolderMissingError(f"Invalid BOX_FOLDER_PATH specified: {BOX_PATH}")

TAB_HIDDEN_NAME = environ.get('WS_HIDDEN_NAME', '{0} Tele Stats').format(_year)
TAB_HIDDEN_RENAME = environ.get('WS_HIDDEN_RENAME', 'Tele Stats')

LAKE_ACCOUNT = environ.get('LAKE_ACCOUNT_NAME', '')
LAKE_KEY = environ.get('LAKE_ACCOUNT_KEY',
                       '')
LAKE_URL = f'https://{LAKE_ACCOUNT}.dfs.core.windows.net/'
LAKE_CONTAINER = environ.get('LAKE_CONTAINER_NAME', 'enterprisedata')
LAKE_PATH = environ.get('LAKE_FOLDER_PATH', 'Raw/BOX Reports')
