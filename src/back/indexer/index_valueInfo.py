class InfoClass:
    def __init__(self, type, position, docid) -> None:
        """
        Initializes an instance of the InfoClass.

        Args:
            type (str): The type of the information.
            position (int): The position of the information.
            docid (int): The document ID associated with the information.

        Returns:
            None
        """
        super().__init__()
        self._type = type
        self._position = position
        self._docid = docid

    def __json__(self):
        """
        Returns a dictionary representation of the InfoClass instance.

        Returns:
            dict: A dictionary representing the InfoClass instance.
        """
        return {
            'type': self._type,
            'position': self._position,
            'docid': self._docid
        }
