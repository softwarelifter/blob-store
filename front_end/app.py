from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)

CORS(app)

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


def generate_blob_name(user_id, container_name, blob_name, chunk_id):
    return f"{chunk_id}_{user_id}_{container_name}_{blob_name}"


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
    chunk_info = allocation_info["chunk_info"]

    # Step 2: Stream the data chunks
    for chunk_id, info in chunk_info.items():
        chunk_data = request.files[f"chunk_{chunk_id}"].read()
        data_node = info["data_node"]
        replicas = info["replicas"]
        storage_blob_name = generate_blob_name(
            user_id, container_name, blob_name, chunk_id
        )

        # Store the primary chunk
        data_node_response = requests.post(
            f"http://{data_node}/store_blob",
            files={
                storage_blob_name: (
                    storage_blob_name,
                    chunk_data,
                )
            },
        )

        if data_node_response.status_code != 201:
            return jsonify({"status": "failure", "error": "Failed to store chunk"}), 500

        # # Store replicas
        # for replica_node in replicas:
        #     replica_response = requests.post(
        #         f"http://{replica_node}/store_blob",
        #         files={
        #             storage_blob_name: (
        #                 storage_blob_name,
        #                 chunk_data,
        #             )
        #         },
        #     )

        #     if replica_response.status_code != 201:
        #         return (
        #             jsonify(
        #                 {"status": "failure", "error": "Failed to store chunk replica"}
        #             ),
        #             500,
        #         )

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
    user_id = request.args.get("user_id")
    container = request.args.get("container")
    blob = request.args.get("blob")
    response = requests.get(
        f"http://{MANAGER_HOST}/get_data",
        params={"container": container, "blob": blob, "user_id": user_id},
    )
    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    blob_data = response.json()
    blob_reponse = {}

    for chunk_id, chunk_info in blob_data["chunk_info"].items():
        storage_blob_name = generate_blob_name(
            user_id, blob_data["container_name"], blob_data["blob_name"], chunk_id
        )
        primary_node = chunk_info["primary_node"]
        chunk_response = requests.get(
            f"http://{primary_node}/retrieve_blob",
            params={"blob_name": storage_blob_name},
        )
        if chunk_response.status_code != 200:
            return jsonify(chunk_response.json()), chunk_response.status_code

        blob_reponse[chunk_id] = chunk_response.json()

    return jsonify(blob_reponse), response.status_code


@app.route("/delete_data", methods=["DELETE"])
def delete_data():
    data = request.get_json()
    response = requests.delete(f"http://{MANAGER_HOST}/delete_data", json=data)
    return jsonify(response.json()), response.status_code


@app.route("/list_blobs", methods=["GET"])
def list_blobs():
    user_id = request.args.get("user_id")
    container = request.args.get("container")
    response = requests.get(
        f"http://{MANAGER_HOST}/list_blobs",
        params={"container": container, "user_id": user_id},
    )
    return jsonify(response.json()), response.status_code


@app.route("/delete_container", methods=["DELETE"])
def delete_container():
    data = request.get_json()
    response = requests.delete(f"http://{MANAGER_HOST}/delete_container", json=data)
    return jsonify(response.json()), response.status_code


@app.route("/list_containers", methods=["GET"])
def list_containers():
    user_id = request.args.get("user_id")
    response = requests.get(
        f"http://{MANAGER_HOST}/list_containers",
        params={"user_id": user_id},
    )
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
