import json
import logging

import azure.functions as func


def main(event: func.EventGridEvent,
         outputBlob: func.Out[func.InputStream]):
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    }, indent=4)
        
    logging.info(f'Saving payload as blob: {result}')
    outputBlob.set(result)

    logging.info('Python EventGrid trigger processed an event')
