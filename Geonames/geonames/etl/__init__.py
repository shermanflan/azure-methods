from datetime import date
from os.path import join
from uuid import uuid4

from geonames import (
    LAKE_CONTAINER, LAKE_CENSUS_PATH, LAKE_GEONAMES_PATH,
    CENSUS_STATE_NAME, CENSUS_COUNTY_NAME,
    GEONAMES_PLACE_NAME, GEONAMES_ZIPCODE_NAME
)
from geonames.api.census import (get_states, get_counties)
from geonames.api.geonames import (get_places, get_zipcodes)
from geonames.api.lake import LakeFactory
from geonames.util.log import get_logger

logger = get_logger(__name__)


def load_datasets(tmp_folder):
    """
    Entrypoint for downloading all geography data sets. Each dataset is
    data wrangled into a DataFrame and then saved locally in parquet
    format. The files are then uploaded to a data lake.

    :param tmp_folder: temporary workspace
    :return: None
    """
    logger.info('Getting geography datasets')

    counties = get_counties()
    states = get_states(counties)
    # places = get_places(tmp_folder)
    zipcodes = get_zipcodes(tmp_folder)

    date_stamp = date.today().strftime('%Y-%m-%d')
    year_stamp = date.today().strftime('%Y')

    logger.info('Saving locally in parquet format')

    states_path = join(tmp_folder
                       , f"{CENSUS_STATE_NAME}_{uuid4()}.parquet")
    logger.debug('Saving states', source=states_path)

    states.to_parquet(path=states_path, engine='fastparquet'
                      , compression='snappy', index=True)

    counties_path = join(tmp_folder
                         , f"{CENSUS_COUNTY_NAME}_{uuid4()}.parquet")
    logger.debug('Saving counties', source=counties_path)

    counties.to_parquet(path=counties_path, engine='fastparquet'
                        , compression='snappy', index=True)

    # places_path = join(tmp_folder
    #                    , f"{GEONAMES_PLACE_NAME}_{date_stamp}.parquet")
    # logger.debug('Saving places', source=places_path)
    # places.to_parquet(path=places_path, engine='fastparquet'
    #                   , compression='snappy')

    zipcodes_path = join(tmp_folder
                         , f"{GEONAMES_ZIPCODE_NAME}_{uuid4()}.parquet")
    logger.debug('Saving zipcodes', source=zipcodes_path)

    zipcodes.to_parquet(path=zipcodes_path, engine='fastparquet'
                        , compression='snappy', index=True)

    logger.info('Uploading to lake')

    lake_paths = [
        (join(LAKE_CENSUS_PATH, CENSUS_COUNTY_NAME, year_stamp)
           , counties_path)
        # , (join(LAKE_GEONAMES_PATH, GEONAMES_PLACE_NAME, year_stamp)
        #    , places_path)
        , (join(LAKE_GEONAMES_PATH, GEONAMES_ZIPCODE_NAME, year_stamp)
           , zipcodes_path)
        , (join(LAKE_CENSUS_PATH, CENSUS_STATE_NAME, year_stamp)
           , states_path)
    ]

    for target, source in lake_paths:
        LakeFactory().upload_files(lake_container=LAKE_CONTAINER,
                                   lake_dir=target,
                                   files=[source])
