import datetime
import logging

import azure.functions as func


def main(req: func.HttpRequest,
         outputEvent: func.Out[func.EventGridOutputEvent]) -> func.HttpResponse:

    logging.info('Python HTTP trigger EventGridPublish processed a request.')

    eventGridEvent = func.EventGridOutputEvent(
        id="test-id",
        data={"tag1": "value1", "tag2": "value2"},
        subject="new-job-1",
        event_type="new-job-event-1",  # needs to exist (I think)
        event_time=datetime.datetime.utcnow(),
        data_version="1.0")

    logging.info(f"eventGridEvent: {eventGridEvent}")

    outputEvent.set(eventGridEvent)

    return func.HttpResponse(f"This HTTP triggered function executed successfully.")
