import pymongo


class MongoDBConnection:
    def __init__(self, host='vmi1224404.contaboserver.net',
                 port=27017,
                 username='m151User',
                 password='YyKOhV1xa3mnmlFP',
                 auth_source='M151',
                 auth_mechanism='DEFAULT'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth_source = auth_source
        self.auth_mechanism = auth_mechanism
        self.client = ''
        self.useNewUrlParser = True
        self.useUnifiedTopology = True

    # Return the connection object
    def get_connection(self):
        if self.username and self.password:
            uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/?authSource={self.auth_source}" \
                  f"&authMechanism={self.auth_mechanism}"
            self.client = pymongo.MongoClient(uri)
        else:
            self.client = pymongo.MongoClient(self.host, self.port)
        return self.client

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()
