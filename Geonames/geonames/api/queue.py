
from azure.storage.queue import QueueClient


class AzureQueueHook:

    def __init__(self, queue_name, connection_string):
        if not queue_name or not connection_string:
            raise Exception("Missing queue credentials")

        self.queue_name = queue_name
        self.connection_string = connection_string
        self.client = None

    def get_connection(self):
        if not self.client:
            self.client = QueueClient.from_connection_string(
                self.connection_string, self.queue_name)

        return self.client

    def send_messages(self, data, count=1):
        for _ in range(count):
            self.get_connection().send_message(data)
