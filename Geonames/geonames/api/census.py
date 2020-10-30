from datetime import datetime
import re

import pandas as pd

from geonames import (
    APP_LOG_KEY,
    CENSUS_STATES_URI,
    CENSUS_COUNTIES_URI
)
from geonames.util.log import get_logger

logger = get_logger(__name__)


def get_counties():
    """
    Downloads US counties from census.gov at:
    - https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html

    Some data wrangling is applied to split the geoid and county name
    columns.

    :return: DataFrame
    """
    logger.info('Downloading counties', source=CENSUS_COUNTIES_URI)

    counties = (
        pd
        .read_table(CENSUS_COUNTIES_URI, dtype={'GEOID': str, 'ANSICODE': str})
        .rename(columns=lambda x: x.strip())
    )

    counties['StateFIPS'] = counties.GEOID.str[:2]
    counties['CountyFIPS'] = counties.GEOID.str[2:]

    county_pattern = re.compile(pattern=r'\sCounty$')

    counties.loc[
        counties.NAME.str.contains(county_pattern)
        , ['CountyPrefix']] = counties.NAME.str.replace(county_pattern, repl='')
    counties.loc[~counties.CountyPrefix.isna(), ['CountySuffix']] = 'COUNTY'
    counties.loc[counties.CountyPrefix.isna(), ['CountyPrefix']] = counties.NAME

    counties['CreatedDateTime'] = datetime.now()
    counties['RecCreatedBy'] = APP_LOG_KEY

    logger.info('Total counties collected', count=counties.shape[0])

    return counties


def get_states(counties):
    """
    Downloads US states from census.gov at:
    - https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html

    The counties DataFrame is used to look up the state abbreviation. In
    addition, the state region and division rows are melted.

    :param counties: Counties DataFrame
    :return: DataFrame
    """
    logger.info('Downloading states', source=CENSUS_STATES_URI)

    states = pd.read_excel(CENSUS_STATES_URI, engine='openpyxl', header=1, skiprows=4,
                           dtype={
                               'Region': str, 'Division': str
                               , 'State (FIPS)': str
                           })

    states_region = states.loc[
        states['Name'].str.endswith('Region')
        , ['Region', 'Name']
    ]

    states_division = states.loc[
        states['Name'].str.endswith('Division')
        , ['Division', 'Name']
    ]

    unity = (
        states
        .loc[states['State (FIPS)'] != '00', :]
        .merge(states_region, on='Region', how='left')
        .merge(states_division, on='Division', how='left')
        .rename(columns={
            'State (FIPS)': 'StateFIPS', 'Name_x': 'StateName',
            'Name_y': 'RegionName', 'Name': 'DivisionName'
        })
        .merge(counties.loc[:, ['StateFIPS', 'USPS']], on='StateFIPS', how='left')
        .drop_duplicates()
        .reset_index(drop=True)
    )

    unity['CreatedDateTime'] = datetime.now()
    unity['RecCreatedBy'] = APP_LOG_KEY

    logger.info('Total states collected', count=states.shape[0])

    return unity
