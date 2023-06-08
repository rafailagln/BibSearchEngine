class InfoClass:
    def __init__(self, _type, position, doc_id) -> None:
        """
        Initializes an instance of the InfoClass.

        Args:
            _type (str): The type of the information.
            position (int): The position of the information.
            doc_id (int): The document ID associated with the information.

        Returns:
            None
        """
        super().__init__()
        self._type = _type
        self._position = position
        self._doc_id = doc_id

    def __json__(self):
        """
        Returns a dictionary representation of the InfoClass instance.

        Returns:
            dict: A dictionary representing the InfoClass instance.
        """
        return {
            'type': self._type,
            'position': self._position,
            'docid': self._doc_id
        }
