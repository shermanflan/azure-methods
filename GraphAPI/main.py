from tempfile import TemporaryDirectory

from graph_api import BLOB_CONTAINER, BLOB_PATH
from graph_api.api.blob import BlobFactory
from graph_api.etl import load_snapshot, load_delta
from graph_api.util.log import get_logger

logger = get_logger(__name__)

if __name__ == '__main__':

    # TODO
    # Consider writing success/failure to Teams
    # Update readme (see here for MD examples):
    #   https://github.com/microsoftgraph?q=&type=&language=python
    #   https://github.com/jd/tenacity

    with TemporaryDirectory() as tmp_dir:

        try:
            save_point = BlobFactory().download_to_file(BLOB_CONTAINER,
                                                        BLOB_PATH,
                                                        tmp_dir)

            if not save_point:
                logger.info(f'Retrieving user snapshot from Graph.')

                load_snapshot(tmp_dir)
            else:
                logger.info(f'Retrieving user delta from Graph.')

                load_delta(save_point, tmp_dir)
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise

    logger.info(f'Completed successfully...')
