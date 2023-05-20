import http.client
import json

def update_node_status(node_id, online):
    status = {"id": node_id, "online": online}
    headers = {'Content-type': 'application/json'}

    connection = http.client.HTTPConnection("localhost", 8080)
    connection.request("POST", "/api/update", body=json.dumps(status), headers=headers)
    response = connection.getresponse()

    # Optionally, you can handle the response here

    connection.close()

update_node_status(1, True)
