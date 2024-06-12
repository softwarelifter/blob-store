import os
import requests
import base64


def create_container(user_id, container_name):
    response = requests.post(
        "http://localhost/create_container",
        json={"user_id": user_id, "container_name": container_name},
    )
    print(response.json())


def put_data(user_id, container_name, blob_name, blob_path, chunk_size=1024 * 1024):
    files = {}

    # Get the blob size from the file
    blob_size = os.path.getsize(blob_path)
    num_chunks = -(-blob_size // chunk_size)

    # Open the file and read it in chunks
    with open(blob_path, "rb") as f:
        for i in range(num_chunks):
            chunk_data = f.read(chunk_size)
            files[f"chunk_{i}"] = (f"{blob_name}_{i}", chunk_data)

    response = requests.post(
        "http://localhost:8080/put_data",
        data={
            "user_id": user_id,
            "container_name": container_name,
            "blob_name": blob_name,
            "blob_size": blob_size,
            "chunk_size": chunk_size,
        },
        files=files,
    )

    print(response.json())


def reconstruct_file(response, output_file_path):
    with open(output_file_path, "wb") as output_file:
        for chunk_id, data in response.json().items():
            # Retrieve each chunk as base64
            base64_chunk = data["blob_data"]
            # Decode the base64 chunk to bytes
            chunk_data = base64.b64decode(base64_chunk)
            # Write the bytes to the output file
            output_file.write(chunk_data)


def get_data(user_id, container_name, blob_name):
    response = requests.get(
        "http://localhost:8080/get_data",
        params={"container": container_name, "blob": blob_name, "user_id": user_id},
    )
    if response.status_code != 200:
        return print(response)
    reconstruct_file(response, f"reconstructed_{blob_name}")
    # print(response.json())


def delete_data(container_name, blob_name):
    response = requests.delete(
        "http://localhost:8080/delete_data",
        json={"container_name": container_name, "blob_name": blob_name},
    )
    print(response.json())


def list_blobs(user_id, container_name):
    response = requests.get(
        "http://localhost:8080/list_blobs",
        params={"container": container_name, "user_id": user_id},
    )
    print(response.json())


def delete_container(container_name):
    response = requests.delete(
        "http://localhost:8080/delete_container",
        json={"container_name": container_name},
    )
    print(response.json())


def list_containers(user_id):
    response = requests.get(
        "http://localhost:8080/list_containers",
        params={"user_id": user_id},
    )
    print(response.json())


# Example usage
if __name__ == "__main__":
    # create_container(1, "my_container")
    # put_data(
    #     1,
    #     "test_container",
    #     "requirements1.txt",
    #     "/Users/suraj/learnings/blob-store/blobstore/suraj1.jpg",
    # )
    get_data(1, "test_container", "requirements1.txt")
    # list_blobs(1, "test_container")
    # delete_data("test_container", "requirements.txt")
    # delete_container("images")
    # list_containers(1)
