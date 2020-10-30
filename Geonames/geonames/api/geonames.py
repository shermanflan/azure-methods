from datetime import datetime
from os.path import join
import re
from zipfile import ZipFile

import numpy as np
import pandas as pd
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type
)
import requests
from requests.exceptions import HTTPError

from geonames import (
    APP_LOG_KEY, GEONAMES_PLACES_URI, GEONAMES_ZIPCODES_URI
)
from geonames.exceptions import RetryableError
from geonames.util.log import get_logger

logger = get_logger(__name__)


# @retry(stop=stop_after_attempt(3),
#        wait=wait_exponential(multiplier=30),
#        retry=retry_if_exception_type(RetryableError))
def get_places(tmp_folder):
    """
    Downloads place names from geonames.org at:
    - https://download.geonames.org/export/dump/

    In order to facilitate matching with zip codes data set, all synonyms
    are exploded into distinct rows. In addition, the modified date
    field is converted to numeric.

    :param tmp_folder: temporary workspace
    :return: DataFrame
    """
    session = requests.Session()
    tmp_zip = join(tmp_folder, 'US-places.zip')

    logger.info('Downloading places', source=GEONAMES_PLACES_URI
                , target=tmp_zip)

    try:
        r = session.get(GEONAMES_PLACES_URI)
        r.raise_for_status()

        with open(tmp_zip, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
    except HTTPError as e:

        logger.error(f'Request error', status_code=r.status_code
                     , source=GEONAMES_PLACES_URI)
        logger.exception(e)

        if e.response.status_code in (429, 503, 504):
            logger.error('Server overloaded')
            raise RetryableError('Retrying places download')

        raise

    tmp_file = join(tmp_folder, 'US.txt')

    logger.debug('Unzipping archive', source=tmp_zip, target=tmp_file)

    with ZipFile(tmp_zip) as z:
        z.extract('US.txt', path=tmp_folder)

    header = [
        'geonameid', 'name', 'ascii_name'
        , 'alternatenames', 'latitude', 'longitude'
        , 'feature_class', 'feature_code', 'country_code'
        , 'cc2', 'admin_code1', 'admin_code2'
        , 'admin_code3', 'admin_code4', 'population'
        , 'elevation', 'dem', 'timezone', 'modification_date'
    ]

    places = (
        pd
        .read_table(tmp_file
                    , names=header
                    , dtype={
                        'admin_code1': str
                        , 'admin_code2': str
                        , 'admin_code3': str
                        , 'admin_code3': str
                    })
        .drop(['admin_code4', 'ascii_name'], axis=1)
    )

    logger.debug('Places collected', count=places.shape[0])

    logger.info('Exploding name synonyms')

    pivot = places.loc[~places.alternatenames.isna(), :]

    places2 = (
        pd
        .DataFrame(data=pivot.alternatenames.str.split(pat=','
                                                       , expand=False)
                   , index=pivot.index)
        .explode('alternatenames')
        .join(places.drop(['name'], axis=1), lsuffix='_tmp')
    )

    logger.debug('Synonyms exploded', count=places2.shape[0])

    places2['name'] = places2.alternatenames_tmp
    places2.drop(['alternatenames_tmp'], axis=1, inplace=True)

    unity = places.append(places2).drop_duplicates()
    unity.modification_date = (
        unity.modification_date.str
        .replace(pat='-', repl='', regex=False)
        .astype(np.int32)
    )
    unity['CreatedDateTime'] = datetime.now()
    unity['RecCreatedBy'] = APP_LOG_KEY

    logger.info('Total places collected', count=unity.shape[0])

    return unity


# @retry(stop=stop_after_attempt(3),
#        wait=wait_exponential(multiplier=30),
#        retry=retry_if_exception_type(RetryableError))
def get_zipcodes(tmp_folder):
    """
    Downloads zipcodes from geonames.org at:
    - http://download.geonames.org/export/zip/

    Some data wrangling is applied to convert the ' Mc .' pattern to
    '.Mc.'.

    :param tmp_folder: temporary workspace
    :return: DataFrame
    """
    session = requests.Session()
    tmp_zip = join(tmp_folder, 'US-zipcodes.zip')

    logger.info('Downloading zipcodes', source=GEONAMES_ZIPCODES_URI
                , target=tmp_zip)

    try:
        r = session.get(GEONAMES_ZIPCODES_URI)
        r.raise_for_status()
    except HTTPError as e:

        logger.error(f'Request error', status_code=r.status_code
                     , source=GEONAMES_PLACES_URI)
        logger.exception(e)

        if e.response.status_code in (429, 503, 504):
            logger.error('Server overloaded')
            raise RetryableError('Retrying places download')

        raise

    with open(tmp_zip, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

    tmp_file = join(tmp_folder, 'US.txt')

    logger.debug('Unzipping archive', source='US.txt', target=tmp_file)

    with ZipFile(tmp_zip) as z:
        z.extract('US.txt', path=tmp_folder)

    header = ['country_code', 'postal_code', 'place_name',
              'admin_name1', 'admin_code1', 'admin_name2',
              'admin_code2', 'admin_name3', 'admin_code3',
              'latitude', 'longitude', 'accuracy']

    zipcodes = pd.read_table(tmp_file, names=header,
                             dtype={'postal_code': str, 'admin_code2': str,
                                    'admin_code3': str, 'accuracy': str})

    cleanse_1 = re.compile(pattern=r'\sMc\s')
    cleanse_2 = re.compile(pattern=r'^Mc\s')

    zipcodes.loc[
        zipcodes.place_name.str.contains(pat=cleanse_1)
        , ['place_name']] = zipcodes.place_name.str.replace(pat=cleanse_1, repl=' Mc')

    zipcodes.loc[
        zipcodes.place_name.str.contains(pat=cleanse_2)
        , ['place_name']] = zipcodes.place_name.str.replace(pat=cleanse_2, repl='Mc')

    zipcodes['CreatedDateTime'] = datetime.now()
    zipcodes['RecCreatedBy'] = APP_LOG_KEY

    logger.info('Total zipcodes collected', count=zipcodes.shape[0])

    return zipcodes
