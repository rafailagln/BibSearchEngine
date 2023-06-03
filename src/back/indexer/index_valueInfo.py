class InfoClass:

    def __init__(self, type, position, docid) -> None:
        """
        Initializes an instance of the InfoClass.

        Inputs:
        - type: The type of the information.
        - position: The position of the information.
        - docid: The document ID associated with the information.

        Outputs: None
        """
        super().__init__()
        self._type = type
        self._position = position
        self._docid = docid

    def __json__(self):
        """
        Returns a dictionary representation of the InfoClass instance.

        Input: None

        Output:
        - A dictionary representing the InfoClass instance.
        """
        return {
            'type': self._type,
            'position': self._position,
            'docid': self._docid
        }
