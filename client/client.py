import requests


def create_container(user_id, container_name):
    response = requests.post(
        "http://localhost/create_container",
        json={"user_id": user_id, "container_name": container_name},
    )
    print(response.json())


def put_data(container_name, blob_name, blob_data):
    response = requests.post(
        "http://localhost/put_data",
        json={
            "container_name": container_name,
            "blob_name": blob_name,
            "blob_data": blob_data,
        },
    )
    print(response.json())


def get_data(container_name, blob_name):
    response = requests.get(
        "http://localhost/get_data",
        params={"container": container_name, "blob": blob_name},
    )
    print(response.json())


def delete_data(container_name, blob_name):
    response = requests.delete(
        "http://localhost/delete_data",
        json={"container_name": container_name, "blob_name": blob_name},
    )
    print(response.json())


def list_blobs(container_name):
    response = requests.get(
        "http://localhost/list_blobs", params={"container": container_name}
    )
    print(response.json())


def delete_container(container_name):
    response = requests.delete(
        "http://localhost/delete_container", json={"container_name": container_name}
    )
    print(response.json())


def list_containers():
    response = requests.get("http://localhost/list_containers")
    print(response.json())


# Example usage
if __name__ == "__main__":
    create_container(1, "my_container")
    put_data("my_container", "my_blob", {"key": "value"})
    get_data("my_container", "my_blob")
    list_blobs("my_container")
    delete_data("my_container", "my_blob")
    delete_container("my_container")
    list_containers()
