from flask import Flask, request, jsonify
import os
from chunk_manager import ChunkManager

app = Flask(__name__)
chunk_manager = ChunkManager()


@app.route("/store_blob", methods=["POST"])
def store_blob():
    data = request.get_json()
    blob_name = data["blob_name"]
    blob_data = data["blob_data"]
    chunk_manager.store_blob(blob_name, blob_data)
    return jsonify({"status": "success"}), 201


@app.route("/retrieve_blob", methods=["GET"])
def retrieve_blob():
    blob_name = request.args.get("blob_name")
    blob_data = chunk_manager.retrieve_blob(blob_name)
    return jsonify({"status": "success", "blob_data": blob_data}), 200


@app.route("/delete_blob", methods=["DELETE"])
def delete_blob():
    blob_name = request.get_json()["blob_name"]
    chunk_manager.delete_blob(blob_name)
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 9001)))
