from flask import Flask, request, jsonify
import psycopg2
import os
import time
from hashlib import sha256
from heartbeat import Heartbeat
import traceback

app = Flask(__name__)

METADATA_STORAGE_HOST = os.getenv("METADATA_STORAGE_HOST", "metadata_storage")
METADATA_STORAGE_PORT = os.getenv("METADATA_STORAGE_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "blobstore")
POSTGRES_USER = os.getenv("POSTGRES_USER", "blobstore_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "blobstore_password")


def connect_to_db():
    print(f"Connecting to database: {METADATA_STORAGE_HOST}:{METADATA_STORAGE_PORT}")
    retries = 0
    db_params = {
        "dbname": POSTGRES_DB,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "host": METADATA_STORAGE_HOST,
        "port": METADATA_STORAGE_PORT,
    }
    while retries < 5:
        try:
            retries += 1
            connection = psycopg2.connect(**db_params)
            print("Connected to database")
            return connection
        except psycopg2.OperationalError:
            print("Database not ready, waiting...")
            traceback.print_exc()
            time.sleep(3)


connection = connect_to_db()


def hash_password(password):
    return sha256(password.encode()).hexdigest()


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data["username"]
    password = hash_password(data["password"])
    cur = connection.cursor()
    cur.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)", (username, password)
    )
    connection.commit()
    return jsonify({"status": "success"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = hash_password(data["password"])
    cur = connection.cursor()
    cur.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, password),
    )
    user = cur.fetchone()
    if user:
        return jsonify({"status": "success", "user_id": user[0]}), 200
    else:
        return (
            jsonify({"status": "failure", "message": "Invalid username or password"}),
            401,
        )


from flask import request, jsonify


@app.route("/create_container", methods=["POST"])
def create_container():
    try:
        data = request.get_json()
        user_id = data["user_id"]
        container_name = data["container_name"]
        print(f"Creating container {container_name} for user {user_id}")
        cur = connection.cursor()
        cur.execute(
            "INSERT INTO containers (name, user_id) VALUES (%s, %s)",
            (container_name, user_id),
        )
        connection.commit()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        # Rollback the transaction if an error occurs
        connection.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500
    finally:
        if "cur" in locals():
            cur.close()  # Close the cursor to release resources


# @app.route("/create_container", methods=["POST"])
# def create_container():
#     data = request.get_json()
#     user_id = data["user_id"]
#     container_name = data["container_name"]
#     print(f"Creating container {container_name} for user {user_id}")
#     cur = connection.cursor()
#     cur.execute(
#         "INSERT INTO containers (name, user_id) VALUES (%s, %s)",
#         (container_name, user_id),
#     )
#     connection.commit()
#     return jsonify({"status": "success"}), 201


# @app.route("/put_data", methods=["POST"])
# def put_data():
#     data = request.get_json()
#     container_name = data["container_name"]
#     blob_name = data["blob_name"]
#     blob_data = data["blob_data"]
#     # Logic to store blob data in data nodes and update metadata
#     return jsonify({"status": "success"}), 200


# @app.route("/get_data", methods=["GET"])
# def get_data():
#     container_name = request.args.get("container")
#     blob_name = request.args.get("blob")
#     # Logic to retrieve blob data from data nodes
#     return jsonify({"status": "success", "data": "blob_data_here"}), 200


# @app.route("/delete_data", methods=["DELETE"])
# def delete_data():
#     data = request.get_json()
#     container_name = data["container_name"]
#     blob_name = data["blob_name"]
#     # Logic to delete blob data from data nodes and update metadata
#     return jsonify({"status": "success"}), 200


# @app.route("/list_blobs", methods=["GET"])
# def list_blobs():
#     container_name = request.args.get("container")
#     # Logic to list all blobs in the container
#     return jsonify({"blobs": []}), 200


# @app.route("/delete_container", methods=["DELETE"])
# def delete_container():
#     data = request.get_json()
#     container_name = data["container_name"]
#     # Logic to delete container and update metadata
#     return jsonify({"status": "success"}), 200


# @app.route("/list_containers", methods=["GET"])
# def list_containers():
#     # Logic to list all containers for a user
#     return jsonify({"containers": []}), 200


if __name__ == "__main__":
    print("starting manager2")
    # heartbeat = Heartbeat()
    # heartbeat.start()
    app.run(host="0.0.0.0", port=8090)
