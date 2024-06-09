import threading
import time
import requests
import os

MANAGER_HOST = os.getenv("MANAGER_HOST")


class Heartbeat(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            # Send heartbeat to manager
            requests.post(
                f"http://{MANAGER_HOST}/heartbeat", json={"node": "data_node1"}
            )
            time.sleep(30)
