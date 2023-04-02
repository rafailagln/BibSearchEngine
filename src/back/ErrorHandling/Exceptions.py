class NoMetadataException(Exception):
    """
    Exception raised for errors of existence of Metadata collection in MongoDB.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message='Νo metadata collection in database'):
        self.message = message
        super().__init__(self.message)
