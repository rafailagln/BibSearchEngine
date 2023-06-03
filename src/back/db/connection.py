import pymongo


class MongoDBConnection:
    def __init__(self, host='localhost',
                 port=27017,
                 username=None,
                 password=None,
                 auth_source='M151',
                 auth_mechanism='DEFAULT'):
        """
        Establishes a connection to a MongoDB database.

        Inputs:
        - host: The hostname or IP address of the MongoDB server.
        - port: The port number of the MongoDB server.
        - username: The username for authentication (optional).
        - password: The password for authentication (optional).
        - auth_source: The authentication source database (optional).
        - auth_mechanism: The authentication mechanism (optional).

        Note: If authentication credentials are provided, they will be used to establish an authenticated connection.

        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth_source = auth_source
        self.auth_mechanism = auth_mechanism
        self.client = ''
        self.useNewUrlParser = True
        self.useUnifiedTopology = True

    def get_connection(self):
        """
        Returns the connection object to the MongoDB database.

        Outputs:
        - Returns the MongoDB client connection object.

        Note: If authentication credentials are provided, an authenticated connection will be returned.
        """
        if self.username and self.password:
            uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/?authSource={self.auth_source}" \
                  f"&authMechanism={self.auth_mechanism}"
            self.client = pymongo.MongoClient(uri)
        else:
            self.client = pymongo.MongoClient(self.host, self.port)
        return self.client

    def __enter__(self):
        """
        Enables the usage of the 'with' statement for the MongoDBConnection class.

        Outputs:
        - Returns the MongoDBConnection object.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes the MongoDB connection when exiting the 'with' statement.

        Inputs:
        - exc_type: The type of exception raised (if any).
        - exc_value: The exception object raised (if any).
        - traceback: The traceback information (if any).
        """
        self.client.close()
