from flask import Flask, request, jsonify
import psycopg2
import os
import time
import uuid
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


def generate_blob_id():
    return str(uuid.uuid4())


DEFAULT_CHUNK_SIZE = 1024 * 1024
DEFAULT_REPLICATION_FACTOR = 3


def split_blob(blob_size, chunk_size=DEFAULT_CHUNK_SIZE):
    num_chunks = -(-blob_size // chunk_size)  # Ceiling division
    return num_chunks


def allocate_data_nodes(
    num_chunks, data_nodes, replication_factor=DEFAULT_REPLICATION_FACTOR
):
    chunk_info = {}
    for i in range(num_chunks):
        primary_node = data_nodes[i % len(data_nodes)]
        replicas = [
            data_nodes[(i + j) % len(data_nodes)] for j in range(1, replication_factor)
        ]
        chunk_info[i] = {"data_node": primary_node, "replicas": replicas}
    return chunk_info


@app.route("/initialize_upload", methods=["POST"])
def initialize_upload():
    data = request.get_json()
    user_id = data["user_id"]
    container_name = data["container_name"]
    blob_name = data["blob_name"]
    blob_size = int(data["blob_size"])
    chunk_size = int(data.get("chunk_size", DEFAULT_CHUNK_SIZE))

    blob_id = generate_blob_id()
    num_chunks = split_blob(blob_size, chunk_size)

    cur = connection.cursor()

    try:
        # Get container_id
        cur.execute(
            "SELECT id FROM containers WHERE name = %s AND user_id = %s",
            (container_name, user_id),
        )
        container_id = cur.fetchone()
        if not container_id:
            return jsonify({"error": "Container not found"}), 404

        # Execute the query to fetch all data node names
        cur.execute("SELECT name FROM data_nodes")
        data_node_names = cur.fetchall()
        if not data_node_names:
            return jsonify({"error": "No data nodes available"}), 500

        # Extract names from tuples
        data_nodes = [row[0] for row in data_node_names]

        chunk_info = allocate_data_nodes(num_chunks, data_nodes)

        # Update metadata storage
        cur.execute(
            "INSERT INTO blobs (blob_id, container_name, blob_name, blob_size) VALUES (%s, %s, %s, %s)",
            (blob_id, container_name, blob_name, blob_size),
        )

        for chunk_id, info in chunk_info.items():
            primary_node = info["data_node"]
            replicas = info["replicas"]
            cur.execute(
                "INSERT INTO chunks (blob_id, chunk_id, chunk_size, primary_node, replicas) VALUES (%s, %s, %s, %s, %s)",
                (blob_id, chunk_id, chunk_size, primary_node, replicas),
            )

        connection.commit()
        return (
            jsonify(
                {
                    "blob_id": blob_id,
                    "chunk_info": chunk_info,
                }
            ),
            200,
        )
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/finalize_upload", methods=["POST"])
def finalize_upload():
    data = request.get_json()
    blob_id = data["blob_id"]
    try:
        # Logic to finalize the upload and update metadata
        cur = connection.cursor()
        cur.execute(
            "UPDATE blobs SET status = 'uploaded' WHERE blob_id = %s", (blob_id,)
        )
        connection.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    # finally:
    # connection.close()


@app.route("/get_data", methods=["GET"])
def get_data():

    try:
        user_id = request.args.get("user_id")
        container_name = request.args.get("container")
        blob_name = request.args.get("blob")
        cur = connection.cursor()
        cur.execute(
            "SELECT b.blob_id, c.name, b.blob_name, b.blob_size, b.status FROM blobs b JOIN containers c ON b.container_name = c.name WHERE c.name = %s AND c.user_id=%s AND b.blob_name = %s",
            (container_name, user_id, blob_name),
        )
        blob = cur.fetchone()
        if not blob:
            return jsonify({"error": "Blob not found"}), 404
        blob_id, container_name, blob_name, blob_size, status = blob
        cur.execute(
            "SELECT chunk_id, chunk_size, primary_node, replicas FROM chunks WHERE blob_id = %s",
            (blob_id,),
        )
        chunks = cur.fetchall()
        chunk_info = {}
        for chunk in chunks:
            chunk_id, chunk_size, primary_node, replicas = chunk
            chunk_info[chunk_id] = {
                "chunk_size": chunk_size,
                "primary_node": primary_node,
                "replicas": replicas,
            }
        return (
            jsonify(
                {
                    "blob_id": blob_id,
                    "container_name": container_name,
                    "blob_name": blob_name,
                    "blob_size": blob_size,
                    "status": status,
                    "chunk_info": chunk_info,
                }
            ),
            200,
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    # finally:
    # cur.close()


@app.route("/delete_data", methods=["DELETE"])
def delete_data():
    data = request.get_json()
    container_name = data.get("container_name")
    blob_name = data.get("blob_name")

    if not container_name or not blob_name:
        return jsonify({"error": "container_name and blob_name are required"}), 400

    try:
        with connection.cursor() as cur:
            cur.execute(
                "UPDATE blobs SET status='deleted' WHERE container_name = %s AND blob_name = %s",
                (container_name, blob_name),
            )
        connection.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/list_blobs", methods=["GET"])
def list_blobs():
    user_id = request.args.get("user_id")
    container_name = request.args.get("container")
    try:
        cur = connection.cursor()
        cur.execute(
            "SELECT b.blob_id, c.name, b.blob_name, b.blob_size, b.status FROM blobs b JOIN containers c ON b.container_name = c.name WHERE c.status != 'deleted' AND b.status !='deleted' AND c.name = %s AND c.user_id=%s",
            (container_name, user_id),
        )
        blobs = cur.fetchone()
        return jsonify({"blobs": blobs}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/delete_container", methods=["DELETE"])
def delete_container():
    data = request.get_json()
    container_name = data.get("container_name")  # Use get to avoid KeyError

    if not container_name:
        return jsonify({"error": "container_name is required"}), 400

    try:
        with connection.cursor() as cur:
            cur.execute(
                "UPDATE blobs SET status='deleted' WHERE container_name = %s",
                (container_name,),
            )
            cur.execute(
                "UPDATE containers SET status='deleted' WHERE name = %s",
                (container_name,),
            )
        connection.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/list_containers", methods=["GET"])
def list_containers():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        cur = connection.cursor()
        cur.execute(
            "SELECT * FROM containers WHERE status != 'deleted' AND user_id = %s",
            (user_id,),
        )
        containers = cur.fetchall()  # Use fetchall to get all matching rows

        cur.close()  # Close the cursor after use

        if not containers:
            return jsonify({"containers": []}), 200
        return jsonify({"containers": containers}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("starting manager2")
    # heartbeat = Heartbeat()
    # heartbeat.start()
    app.run(host="0.0.0.0", port=8090)
