import os
import json


class ChunkManager:
    def __init__(self):
        self.data_path = "/data"

    def store_blob(self, blob_name, blob_data):
        blob_path = os.path.join(self.data_path, blob_name)
        with open(blob_path, "w") as blob_file:
            json.dump(blob_data, blob_file)

    def retrieve_blob(self, blob_name):
        blob_path = os.path.join(self.data_path, blob_name)
        with open(blob_path, "r") as blob_file:
            return json.load(blob_file)

    def delete_blob(self, blob_name):
        blob_path = os.path.join(self.data_path, blob_name)
        if os.path.exists(blob_path):
            os.remove(blob_path)
