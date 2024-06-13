import os
import json


class ChunkManager:
    def __init__(self):
        self.data_path = "/data"

    def store_blob(self, blob_name, blob_data):
        blob_path = os.path.join(self.data_path, blob_name)

        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(blob_path), exist_ok=True)
            print(f"lenght of blob_data: {len(blob_data)}")
            print(f"blob_data: {blob_data}")

            # Ensure the data is written as bytes
            with open(blob_path, "wb") as blob_file:
                blob_file.write(blob_data)

            print(f"Blob '{blob_name}' stored successfully at '{blob_path}'")
        except Exception as e:
            print(f"Failed to store blob '{blob_name}': {e}")

    def retrieve_blob(self, blob_name):
        blob_path = os.path.join(self.data_path, blob_name)

        with open(blob_path, "rb") as blob_file:  # Open in binary read mode
            return blob_file.read()

    def delete_blob(self, blob_name):
        blob_path = os.path.join(self.data_path, blob_name)
        if os.path.exists(blob_path):
            os.remove(blob_path)
