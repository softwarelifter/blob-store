import os
import json


class ChunkManager:
    def __init__(self):
        self.data_path = "/data"

    def store_blob(self, blob_name, blob_data):
        blob_path = os.path.join(self.data_path, blob_name)

        # Create directories if they don't exist
        os.makedirs(os.path.dirname(blob_path), exist_ok=True)

        # Convert bytes to a JSON-serializable format
        if isinstance(blob_data, bytes):
            blob_data = blob_data.decode("utf-8")  # Assuming UTF-8 encoding

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
