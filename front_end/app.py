from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

MANAGER_HOST = os.getenv("MANAGER_HOST")


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    response = requests.post(f"http://{MANAGER_HOST}/signup", json=data)
    return jsonify(response.json()), response.status_code


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    response = requests.post(f"http://{MANAGER_HOST}/login", json=data)
    return jsonify(response.json()), response.status_code


@app.route("/create_container", methods=["POST"])
def create_container():
    data = request.get_json()
    response = requests.post(f"http://{MANAGER_HOST}/create_container", json=data)
    return jsonify(response.json()), response.status_code


@app.route("/put_data", methods=["POST"])
def put_data():
    user_id = request.form.get("user_id")
    container_name = request.form.get("container_name")
    blob_name = request.form.get("blob_name")
    blob_size = request.form.get("blob_size")

    # Step 1: Initialize the upload and get chunk allocation info
    manager_response = requests.post(
        f"http://{MANAGER_HOST}/initialize_upload",
        json={
            "container_name": container_name,
            "blob_name": blob_name,
            "blob_size": blob_size,
            "user_id": user_id,
        },
    )

    if manager_response.status_code != 200:
        return jsonify({"status": "failure", "error": manager_response.json()}), 500

    allocation_info = manager_response.json()
    blob_id = allocation_info["blob_id"]
    container_id = allocation_info["container_id"]
    chunk_info = allocation_info["chunk_info"]

    # Step 2: Stream the data chunks
    for chunk_id, info in chunk_info.items():
        chunk_data = request.files[f"chunk_{chunk_id}"].read()
        data_node = info["data_node"]
        replicas = info["replicas"]

        # Store the primary chunk
        data_node_response = requests.post(
            f"http://{data_node}/store_blob",
            files={
                "blob_name": (None, f"{user_id}_{container_id}_{blob_name}_{chunk_id}"),
                "blob_data": (None, chunk_data),
            },
        )

        if data_node_response.status_code != 201:
            return jsonify({"status": "failure", "error": "Failed to store chunk"}), 500

        # Store replicas
        for replica_node in replicas:
            replica_response = requests.post(
                f"http://{replica_node}/store_blob",
                files={
                    "blob_name": (
                        None,
                        f"{user_id}_{container_id}_{blob_name}_{chunk_id}",
                    ),
                    "blob_data": (None, chunk_data),
                },
            )

            if replica_response.status_code != 201:
                return (
                    jsonify(
                        {"status": "failure", "error": "Failed to store chunk replica"}
                    ),
                    500,
                )

    # Step 3: Finalize the upload
    finalize_response = requests.post(
        f"http://{MANAGER_HOST}/finalize_upload", json={"blob_id": blob_id}
    )

    if finalize_response.status_code != 200:
        return jsonify({"status": "failure", "error": finalize_response.json()}), 500

    return (
        jsonify({"status": "success", "blob_path": f"{container_name}/{blob_name}"}),
        200,
    )


@app.route("/get_data", methods=["GET"])
def get_data():
    container = request.args.get("container")
    blob = request.args.get("blob")
    response = requests.get(
        f"http://{MANAGER_HOST}/get_data", params={"container": container, "blob": blob}
    )
    return jsonify(response.json()), response.status_code


@app.route("/delete_data", methods=["DELETE"])
def delete_data():
    data = request.get_json()
    response = requests.delete(f"http://{MANAGER_HOST}/delete_data", json=data)
    return jsonify(response.json()), response.status_code


@app.route("/list_blobs", methods=["GET"])
def list_blobs():
    container = request.args.get("container")
    response = requests.get(
        f"http://{MANAGER_HOST}/list_blobs", params={"container": container}
    )
    return jsonify(response.json()), response.status_code


@app.route("/delete_container", methods=["DELETE"])
def delete_container():
    data = request.get_json()
    response = requests.delete(f"http://{MANAGER_HOST}/delete_container", json=data)
    return jsonify(response.json()), response.status_code


@app.route("/list_containers", methods=["GET"])
def list_containers():
    response = requests.get(f"http://{MANAGER_HOST}/list_containers")
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
