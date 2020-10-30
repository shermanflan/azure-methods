from tempfile import TemporaryDirectory

from geonames.etl import load_datasets
from geonames.util.log import get_logger

logger = get_logger(__name__)


if __name__ == '__main__':

    with TemporaryDirectory() as tmp_folder:

        try:
            load_datasets(tmp_folder)
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise

    logger.info(f'Completed successfully')