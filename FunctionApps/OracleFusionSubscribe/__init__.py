from datetime import datetime
import json
import logging
import os

import azure.functions as func

from utility.api.lake import DataLakeHook

lake_client = DataLakeHook(
    lake_url=os.environ['LAKE_URL'], 
    lake_key=os.environ['LAKE_KEY'])


def main(event: func.EventGridEvent,
         outputBlob: func.Out[func.InputStream]):
        
    data = event.get_json()
    logging.info(f"Type: {type(data)}, {data.get('file_name_prefix', None)}")

    result = json.dumps({
        'id': event.id,
        'data': data,
        'data_type': str(type(data)),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    }, indent=4)

    logging.info(f'Saving payload as blob: {result}')

    outputBlob.set(result)

    logging.info(f'Saving to data lake: {result}')

    file_name = f"test-{datetime.now().strftime('%Y-%m-%dT%H-%M-%SZ')}.dat"

    lake_client.upload_data(
        lake_container='event-grid-subscribe', 
        lake_dir='output', 
        file_name=file_name,
        data=result)

    logging.info('Python EventGrid trigger processed an event: {result}')
