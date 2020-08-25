

class XlsxFormatError(Exception):
    """Exception raised for errors in a Excel file.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message
