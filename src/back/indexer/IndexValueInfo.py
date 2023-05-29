class InfoClass:

    def __init__(self, type, position, docid) -> None:
        super().__init__()
        self._type = type
        self._position = position
        self._docid = docid

    def __json__(self):
        return {
            'type': self._type,
            'position': self._position,
            'docid': self._docid
        }
