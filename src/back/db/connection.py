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

        Args:
            host (str): The hostname or IP address of the MongoDB server.
            port (int): The port number of the MongoDB server.
            username (str): The username for authentication (optional).
            password (str): The password for authentication (optional).
            auth_source (str): The authentication source database (optional).
            auth_mechanism (str): The authentication mechanism (optional).

        Note:
            If authentication credentials are provided, they will be used to establish an authenticated connection.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth_source = auth_source
        self.auth_mechanism = auth_mechanism
        self.client = None
        self.useNewUrlParser = True
        self.useUnifiedTopology = True

    def get_connection(self):
        """
        Returns the connection object to the MongoDB database.

        Returns:
            pymongo.MongoClient: The MongoDB client connection object.

        Note:
            If authentication credentials are provided, an authenticated connection will be returned.
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

        Returns:
            MongoDBConnection: The MongoDBConnection object.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes the MongoDB connection when exiting the 'with' statement.

        Args:
            exc_type (type): The type of exception raised (if any).
            exc_value (Exception): The exception object raised (if any).
            traceback (Traceback): The traceback information (if any).
        """
        if isinstance(self.client, pymongo.MongoClient):
            self.client.close()
