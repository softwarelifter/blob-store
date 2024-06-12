from flask import Flask, request, jsonify
import base64
import os
from chunk_manager import ChunkManager
import traceback

app = Flask(__name__)
chunk_manager = ChunkManager()


@app.route("/store_blob", methods=["POST"])
def store_blob():
    try:
        for key, value in request.files.items():
            print("Request received")
            blob_name = key
            blob_data = value.read()
            print("data loaded")
            chunk_manager.store_blob(blob_name, blob_data)
    except Exception:
        traceback.print_exc()
        return jsonify({"status": "failure"}), 500
    return jsonify({"status": "success"}), 201


@app.route("/retrieve_blob", methods=["GET"])
def retrieve_blob():
    blob_name = request.args.get("blob_name")
    blob_data = chunk_manager.retrieve_blob(blob_name)
    encoded_blob_data = base64.b64encode(blob_data).decode("utf-8")
    return jsonify({"status": "success", "blob_data": encoded_blob_data}), 200


@app.route("/delete_blob", methods=["DELETE"])
def delete_blob():
    blob_name = request.get_json()["blob_name"]
    chunk_manager.delete_blob(blob_name)
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 9001)))
