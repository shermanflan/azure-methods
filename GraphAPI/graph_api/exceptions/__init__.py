

class RetryableError(Exception):
    def __init__(self, message, retry_after=10):
        super().__init__(message)

        self.retry_after = retry_after
