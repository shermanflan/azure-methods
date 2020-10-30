from os import environ
import os.path

APP_INSIGHTS_KEY = environ.get('APP_INSIGHTS_KEY', '')
APP_LOG_KEY = environ.get('APP_LOG_KEY', 'bhs.aci.geonames2lake.dev')
LOG_LEVEL = environ.get('LOG_LEVEL', 'DEBUG')

CENSUS_STATES_URI = environ.get('CENSUS_STATES_URI'
                                , 'https://www2.census.gov/programs-surveys/popest/geographies/2019/state-geocodes-v2019.xlsx')
CENSUS_COUNTIES_URI = environ.get('CENSUS_COUNTIES_URI'
                                  , 'https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2019_Gazetteer/2019_Gaz_counties_national.zip')
GEONAMES_PLACES_URI = environ.get('GEONAMES_PLACES_URI'
                                  , 'https://download.geonames.org/export/dump/US.zip')
GEONAMES_ZIPCODES_URI = environ.get('GEONAMES_ZIPCODES_URI'
                                    , 'http://download.geonames.org/export/zip/US.zip')
CENSUS_STATE_NAME = environ.get('CENSUS_STATE_NAME', 'MasterData.StateTerritory')
CENSUS_COUNTY_NAME = environ.get('CENSUS_COUNTY_NAME', 'MasterData.CountyProvince')
GEONAMES_PLACE_NAME = environ.get('GEONAMES_PLACE_NAME', 'MasterData.GeoPlace')
GEONAMES_ZIPCODE_NAME = environ.get('GEONAMES_ZIPCODE_NAME', 'MasterData.ZipCode')

_STORE_ACCOUNT = environ.get('LAKE_ACCOUNT_NAME', 'pahintegrationstorage')
STORE_KEY = environ.get('LAKE_ACCOUNT_KEY', '')

LAKE_URL = f'https://{_STORE_ACCOUNT}.dfs.core.windows.net'
LAKE_CONTAINER = environ.get('LAKE_CONTAINER_NAME', 'enterprisedata')
_LAKE_BASE = environ.get('LAKE_BASE_PATH', 'Raw/Master Data/Geography/Brightspring')
LAKE_CENSUS_PATH = os.path.join(_LAKE_BASE, 'census.gov/Table')
LAKE_GEONAMES_PATH = os.path.join(_LAKE_BASE, 'geonames.org/Table')