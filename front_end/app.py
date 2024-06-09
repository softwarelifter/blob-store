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
    data = request.get_json()
    response = requests.post(f"http://{MANAGER_HOST}/put_data", json=data)
    return jsonify(response.json()), response.status_code


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
