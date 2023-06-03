import http.client
import base64
import json
from urllib.parse import urlparse

class APIRequester:
    """
    Sends a POST request to the 'update_config' endpoint of the specified base URL.

    Inputs:
    - data: A dictionary containing the configuration data to be sent in the request body.

    Outputs:
    - If the request is successful (status code 200), returns the parsed JSON response.
    - Otherwise, raises an exception with the corresponding status code.
    """
    def __init__(self, base_url, username, password):
        self.parsed_url = urlparse(base_url)
        self.auth = base64.b64encode(f"{username}:{password}".encode()).decode()

    def post_update_config_endpoint(self, data):
        conn = http.client.HTTPConnection(self.parsed_url.netloc)
        path = f"{self.parsed_url.path}/update_config"
        headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json"
        }

        conn.request("POST", path, body=json.dumps(data), headers=headers)

        response = conn.getresponse()

        if response.status == 200:
            return json.loads(response.read().decode())
        else:
            raise Exception(f"Request failed with status {response.status}")
