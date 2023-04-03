import pymongo

class MongoDBConnection:
    def __init__(self, host='vmi1224404.contaboserver.net',
                 port=27017,
                 username='m151DevUser',
                 password='YyKOhV1xa3mnmlFP',
                 auth_source='M151Dev',
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

# mongodb://m151User:YyKOhV1xa3mnmlFP@vmi1224404.contaboserver.net:27017/?authMechanism=DEFAULT&authSource=M151
    def __enter__(self):
        if self.username and self.password:
            uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/?authSource={self.auth_source}&authMechanism={self.auth_mechanism}, {self.useNewUrlParser}"
            self.client = pymongo.MongoClient(uri)


        else:
            self.client = pymongo.MongoClient(self.host, self.port)
        db = self.client['M151Dev']  # Replace with the name of your database
        return db['Papers']  # Return the Papers collection

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()
