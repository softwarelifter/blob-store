from flask import Flask, request, jsonify, Response, make_response, stream_with_context
from flask_cors import CORS
import traceback
import requests
import os

app = Flask(__name__)

CORS(app)

MANAGER_HOST = os.getenv("MANAGER_HOST")


@app.route("/is-logged-in", methods=["GET"])
def is_logged_in():
    response = requests.get(
        f"http://{MANAGER_HOST}/is-logged-in", headers=request.headers
    )
    return jsonify(response.json()), response.status_code


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    response = requests.post(
        f"http://{MANAGER_HOST}/signup", json=data, headers=request.headers
    )
    return jsonify(response.json()), response.status_code


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    response = requests.post(
        f"http://{MANAGER_HOST}/login", json=data, headers=request.headers
    )
    return jsonify(response.json()), response.status_code


@app.route("/logout", methods=["POST"])
def logout():
    print("Request headers:", request.headers)
    response = requests.post(f"http://{MANAGER_HOST}/logout", headers=request.headers)
    return jsonify(response.json()), response.status_code


@app.route("/create_container", methods=["POST"])
def create_container():
    data = request.get_json()
    response = requests.post(
        f"http://{MANAGER_HOST}/create_container", json=data, headers=request.headers
    )
    return jsonify(response.json()), response.status_code


def generate_blob_name(user_id, container_name, blob_name, chunk_id):
    return f"{chunk_id}_{user_id}_{container_name}_{blob_name}"


def generate_chunk_name(upload_id, part_number):
    return f"{upload_id}_{part_number}"


@app.route("/initiate-upload", methods=["POST"])
def initiate_upload():
    data = request.get_json()
    response = requests.post(
        f"http://{MANAGER_HOST}/initiate_upload", json=data, headers=request.headers
    )
    return jsonify(response.json()), response.status_code


@app.route("/upload-part", methods=["POST"])
def upload_part():
    try:
        print("Request headers:", request.headers)
        print("Request form:", request.form)
        print("Request files:", request.files)
        if "file" not in request.files:
            print("no file part in request")
            return (
                jsonify({"status": "failure", "error": "No file part in the request"}),
                400,
            )
        upload_id = request.form.get("upload_id")
        part_number = request.form.get("part_number")
        data_node = request.form.get("data_node")
        chunk = request.files.get("file").read()
        chunk_name = generate_chunk_name(upload_id, part_number)
        # Print the length of the binary data (optional)
        print("Received chunk length:", len(chunk))

        # Print the binary data itself (as bytes)
        print("Received chunk:", chunk)
        # Store the primary chunk
        data_node_response = requests.post(
            f"http://{data_node}/store_blob",
            files={
                chunk_name: (
                    chunk_name,
                    chunk,
                )
            },
        )

        if data_node_response.status_code != 201:
            return jsonify({"status": "failure", "error": "Failed to store chunk"}), 500

        return jsonify({"status": "success"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "failure", "error": str(e)}), 500


@app.route("/complete-upload", methods=["POST"])
def complete_upload():
    data = request.get_json()
    response = requests.post(
        f"http://{MANAGER_HOST}/complete-upload", json=data, headers=request.headers
    )
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
        headers=request.headers,
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
        f"http://{MANAGER_HOST}/finalize_upload",
        json={"blob_id": blob_id},
        headers=request.headers,
    )

    if finalize_response.status_code != 200:
        return jsonify({"status": "failure", "error": finalize_response.json()}), 500

    return (
        jsonify({"status": "success", "blob_path": f"{container_name}/{blob_name}"}),
        200,
    )


@app.route("/download", methods=["GET"])
def download_blob():
    user_id = request.args.get("user_id")
    container = request.args.get("container")
    blob = request.args.get("blob")
    response = requests.get(
        f"http://{MANAGER_HOST}/get_data",
        params={"container": container, "blob": blob, "user_id": user_id},
        headers=request.headers,
    )
    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    blob_data = response.json()

    def generate():
        for chunk_id, chunk_info in blob_data["chunk_info"].items():
            storage_blob_name = generate_chunk_name(blob_data["blob_id"], chunk_id)
            primary_node = chunk_info["primary_node"]
            chunk_response = requests.get(
                f"http://{primary_node}/retrieve_blob",
                params={"blob_name": storage_blob_name},
            )

            yield chunk_response.json().get("blob_data")

    # data = generate()
    response = Response(stream_with_context(generate()))
    response.headers["Content-Type"] = "application/octet-stream"
    response.headers["Content-Disposition"] = 'attachment; filename="{}"'.format(
        blob_data["blob_name"]
    )
    return response


@app.route("/get_data", methods=["GET"])
def get_data():
    user_id = request.args.get("user_id")
    container = request.args.get("container")
    blob = request.args.get("blob")
    response = requests.get(
        f"http://{MANAGER_HOST}/get_data",
        params={"container": container, "blob": blob, "user_id": user_id},
        headers=request.headers,
    )
    if response.status_code != 200:
        return jsonify(response.json()), response.status_code

    blob_data = response.json()
    blob_reponse = {}

    for chunk_id, chunk_info in blob_data["chunk_info"].items():
        storage_blob_name = generate_chunk_name(blob_data["blob_id"], chunk_id)
        primary_node = chunk_info["primary_node"]
        chunk_response = requests.get(
            f"http://{primary_node}/retrieve_blob",
            params={"blob_name": storage_blob_name},
        )
        if chunk_response.status_code != 200:
            return jsonify(chunk_response.json()), chunk_response.status_code

        blob_reponse[chunk_id] = chunk_response.json()

    return jsonify(blob_reponse), response.status_code


@app.route("/delete-blob", methods=["DELETE"])
def delete_blob():
    data = request.args
    response = requests.delete(
        f"http://{MANAGER_HOST}/delete_data", params=data, headers=request.headers
    )
    for chunk in response.json().get("chunks", []):
        chunk_name = generate_chunk_name(chunk.get("blob_id"), chunk.get("chunk_id"))
        print("chunk_name", chunk_name)
        res = requests.delete(
            f"http://{chunk.get('primary_node')}/delete_blob",
            params={"chunk_name": chunk_name},
        )
        res = res.json()
        print(
            res.get("status"),
            res.get("chunk_name"),
        )
        # for replica in chunk.get("replicas", []):
        #     requests.delete(
        #         f"http://{replica}/delete_blob",
        #         params={chunk_name: chunk_name},
        #     )
    return jsonify(response.json()), response.status_code


@app.route("/list_blobs", methods=["GET"])
def list_blobs():
    user_id = request.args.get("user_id")
    container = request.args.get("container")
    response = requests.get(
        f"http://{MANAGER_HOST}/list_blobs",
        params={"container": container, "user_id": user_id},
        headers=request.headers,
    )
    return jsonify(response.json()), response.status_code


@app.route("/delete_container", methods=["DELETE"])
def delete_container():
    data = request.args
    response = requests.delete(
        f"http://{MANAGER_HOST}/delete_container", params=data, headers=request.headers
    )
    for chunk in response.json().get("chunks", []):
        chunk_name = generate_chunk_name(chunk.get("blob_id"), chunk.get("chunk_id"))
        print("chunk_name", chunk_name)
        res = requests.delete(
            f"http://{chunk.get('primary_node')}/delete_blob",
            params={"chunk_name": chunk_name},
        )
        res = res.json()
        print(
            res.get("status"),
            res.get("chunk_name"),
        )
        # for replica in chunk.get("replicas", []):
        #     requests.delete(
        #         f"http://{replica}/delete_blob",
        #         params={chunk_name: chunk_name},
        #     )
    return jsonify(response.json()), response.status_code


@app.route("/list_containers", methods=["GET"])
def list_containers():
    user_id = request.args.get("user_id")
    response = requests.get(
        f"http://{MANAGER_HOST}/list_containers",
        params={"user_id": user_id},
        headers=request.headers,
    )
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
