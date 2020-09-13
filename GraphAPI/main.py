from tempfile import TemporaryDirectory

from graph_api import BLOB_CONTAINER, BLOB_PATH
from graph_api.api.blob import BlobFactory
from graph_api.etl import EtlOperations
from graph_api.util.log import logger


if __name__ == '__main__':

    # TODO
    # Consider writing success/failure to Teams
    # Create postman collection and add to git
    # Update readme (see here for MD examples):
    #   https://github.com/microsoftgraph?q=&type=&language=python
    #   https://github.com/jd/tenacity

    # Handle retry-able graph errors:
    #   https://docs.microsoft.com/en-us/graph/errors
    # Handle throttling: HTTP 429, Retry-After in response
    #   https://docs.microsoft.com/en-us/azure/architecture/patterns/throttling
    # Handle server busy: HTTP 503/504, use exponential backoff
    # Handle bandwidth exceeded: HTTP 509, fatal
    # Handle retry-able requests errors:
    #   https://requests.readthedocs.io/en/latest/api/#requests.RequestException

    with TemporaryDirectory() as tmp_dir:

        try:
            save_point = BlobFactory().download_to_file(BLOB_CONTAINER,
                                                        BLOB_PATH,
                                                        tmp_dir)
            ops = EtlOperations()

            if not save_point:
                logger.info(f'Retrieving user snapshot from Graph.')

                ops.load_snapshot(tmp_dir)
            else:
                logger.info(f'Retrieving user delta from Graph.')

                ops.load_delta(save_point, tmp_dir)
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise

    logger.info(f'Completed successfully...')
