import json
from tempfile import TemporaryDirectory
from uuid import uuid4

from geonames import ON_QUEUE, QUEUE_NAME, STORE_CONNECTION
from geonames.api.queue import AzureQueueHook
from geonames.etl import load_datasets
from geonames.util.log import get_logger

logger = get_logger(__name__)

if __name__ == '__main__':

    try:
        if ON_QUEUE:
            logger.info(f"Processing queue item")

            client = AzureQueueHook(QUEUE_NAME, STORE_CONNECTION)

            # Setup work queue
            # client.send_messages(
            #     data=json.dumps({
            #         "id": str(uuid4()),
            #         "test_key": "test_val1",
            #         "test_key2": "test_val2"
            #     }),
            #     count=10
            # )

            message = client.get_connection().receive_message(
                visibility_timeout=5, timeout=15
            )
            if message:
                content = {
                    "id": message.id,
                    "inserted_on": str(message.inserted_on),
                    "expires_on": str(message.expires_on),
                    "dequeue_count": message.dequeue_count,
                    "pop_receipt": message.pop_receipt,
                    "next_visible_on": str(message.next_visible_on),
                    "content": message.content
                }
                logger.info(f"Received: {json.dumps(content, indent=4)}")

                with TemporaryDirectory() as tmp_folder:
                    load_datasets(tmp_folder)

                client.get_connection().delete_message(
                    message=message.id,
                    pop_receipt=message.pop_receipt,
                    timeout=15
                )
        else:
            logger.info(f"Processing")
            with TemporaryDirectory() as tmp_folder:
                load_datasets(tmp_folder)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

    logger.info(f'Completed successfully')