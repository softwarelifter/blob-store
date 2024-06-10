import requests


def create_container(user_id, container_name):
    response = requests.post(
        "http://localhost/create_container",
        json={"user_id": user_id, "container_name": container_name},
    )
    print(response.json())


def put_data(container_name, blob_name, blob_size, chunk_size=1024 * 1024):
    files = {}
    num_chunks = -(-blob_size // chunk_size)

    # Open the file and read it in chunks
    with open(blob_name, "rb") as f:
        for i in range(num_chunks):
            chunk_data = f.read(chunk_size)
            files[f"chunk_{i}"] = (f"{blob_name}_{i}", chunk_data)

    response = requests.post(
        "http://localhost:8080/put_data",
        data={
            "container_name": container_name,
            "blob_name": blob_name,
            "blob_size": blob_size,
            "chunk_size": chunk_size,
        },
        files=files,
    )

    print(response.json())


# def get_data(container_name, blob_name):
#     response = requests.get(
#         "http://localhost/get_data",
#         params={"container": container_name, "blob": blob_name},
#     )
#     print(response.json())


# def delete_data(container_name, blob_name):
#     response = requests.delete(
#         "http://localhost/delete_data",
#         json={"container_name": container_name, "blob_name": blob_name},
#     )
#     print(response.json())


# def list_blobs(container_name):
#     response = requests.get(
#         "http://localhost/list_blobs", params={"container": container_name}
#     )
#     print(response.json())


# def delete_container(container_name):
#     response = requests.delete(
#         "http://localhost/delete_container", json={"container_name": container_name}
#     )
#     print(response.json())


# def list_containers():
#     response = requests.get("http://localhost/list_containers")
#     print(response.json())


# Example usage
if __name__ == "__main__":
    # create_container(1, "my_container")
    put_data(
        "test_container",
        "/Users/suraj/learnings/blob-store/blobstore/client/requirements.txt",
        50000000,
    )
    # get_data("my_container", "my_blob")
    # list_blobs("my_container")
    # delete_data("my_container", "my_blob")
    # delete_container("my_container")
    # list_containers()
