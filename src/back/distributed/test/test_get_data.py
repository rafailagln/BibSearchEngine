import json
import time

from distributed.utils import send_request


def main():
    start_time = time.time()
    node1_addr = ('localhost', 9093)
    # Insert key-value pairs
    insert_request = \
        {'action': 'get_data', 'forwarded': False, 'ids': list(range(1, 10))}
    response = send_request(node1_addr, insert_request)
    print(f"Insert response: {response['results']}")
    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")


if __name__ == '__main__':
    main()
