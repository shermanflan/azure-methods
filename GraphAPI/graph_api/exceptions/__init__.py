

class RetryableError(Exception):
    def __init__(self, message, retry_after):
        super().__init__(message)

        self.retry_after = retry_after


class RetryExceededError(Exception):
    def __init__(self, message):
        super().__init__(message)
