class NoMetadataException(Exception):
    """
    Exception raised for errors of existence of Metadata collection in MongoDB.

    Attributes:
        message (str): Explanation of the error
    """

    def __init__(self, message='Νo metadata collection in database'):
        """
        Initializes a new instance of the NoMetadataException class.

        Args:
            message (str): Explanation of the error (default: 'Νo metadata collection in database')
        """
        self.message = message
        super().__init__(self.message)
