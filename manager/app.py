from flask import Flask, request, jsonify, session
import os
import uuid

from heartbeat import Heartbeat
import traceback

from login import auth_bp, auth_required
from database_connection import DatabaseConnection

app = Flask(__name__)
app.register_blueprint(auth_bp)

app.config["METADATA_STORAGE_HOST"] = os.getenv(
    "METADATA_STORAGE_HOST", "metadata_storage"
)
app.config["METADATA_STORAGE_PORT"] = os.getenv("METADATA_STORAGE_PORT", "5432")
app.config["POSTGRES_DB"] = os.getenv("POSTGRES_DB", "blobstore")
app.config["POSTGRES_USER"] = os.getenv("POSTGRES_USER", "blobstore_user")
app.config["POSTGRES_PASSWORD"] = os.getenv("POSTGRES_PASSWORD", "blobstore_password")
app.secret_key = os.getenv("SECRET_KEY", "secret")


# def connect_to_db():
#     print(f"Connecting to database: {METADATA_STORAGE_HOST}:{METADATA_STORAGE_PORT}")
#     retries = 0
#     db_params = {
#         "dbname": POSTGRES_DB,
#         "user": POSTGRES_USER,
#         "password": POSTGRES_PASSWORD,
#         "host": METADATA_STORAGE_HOST,
#         "port": METADATA_STORAGE_PORT,
#     }
#     while retries < 5:
#         try:
#             retries += 1
#             connection = psycopg2.connect(**db_params)
#             print("Connected to database")
#             return connection
#         except psycopg2.OperationalError:
#             print("Database not ready, waiting...")
#             traceback.print_exc()
#             time.sleep(3)


# connection = connect_to_db()


@app.route("/create_container", methods=["POST"])
@auth_required
def create_container():
    try:
        data = request.get_json()
        print(f"Data: {data}")
        user_id = session["user_id"]
        print(f"User ID: {user_id}")
        container_name = data["container_name"]
        print(f"Creating container: {container_name}")
        db = DatabaseConnection.get_instance()
        db.write(
            "INSERT INTO containers (name, user_id) VALUES (%s, %s)",
            (container_name, user_id),
        )
        return jsonify({"status": "success"}), 201
    except Exception as e:
        traceback.print_exc()
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
        # not replicating for now
        chunk_info[i] = {"data_node": primary_node, "replicas": []}
    return chunk_info


@app.route("/initiate_upload", methods=["POST"])
@auth_required
def initiate_upload():

    try:
        data = request.get_json()
        user_id = session["user_id"]
        container_name = data["container_name"]
        chunk_size = int(data.get("chunk_size", DEFAULT_CHUNK_SIZE))

        blob_name = data["file_name"]
        blob_size = int(data["file_size"])

        blob_id = generate_blob_id()
        num_chunks = split_blob(blob_size, chunk_size)
        db = DatabaseConnection.get_instance()
        container = db.read_one(
            "SELECT id FROM containers WHERE name = %s AND user_id = %s",
            (container_name, user_id),
        )
        if not container:
            return jsonify({"error": "Container not found"}), 404
        data_node_names = db.read_all("SELECT name FROM data_nodes")
        if not data_node_names:
            return jsonify({"error": "No data nodes available"}), 500

        # Extract names from tuples
        data_nodes = [row[0] for row in data_node_names]

        chunk_info = allocate_data_nodes(num_chunks, data_nodes)

        db.write(
            "INSERT INTO blobs (blob_id, container_id, user_id, blob_name, blob_size) VALUES (%s, %s, %s, %s, %s)",
            (blob_id, container[0], user_id, blob_name, blob_size),
        )
        chunk_tuples = [
            ((blob_id, chunk_id, chunk_size, info["data_node"], info["replicas"]))
            for chunk_id, info in chunk_info.items()
        ]
        db.write_many(
            "INSERT INTO chunks (blob_id, chunk_id, chunk_size, primary_node, replicas) VALUES (%s, %s, %s, %s, %s)",
            chunk_tuples,
        )
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
        return jsonify({"error": str(e)}), 500


@app.route("/complete-upload", methods=["POST"])
@auth_required
def complete_upload():
    try:
        data = request.get_json()
        blob_id = data["blob_id"]
        db = DatabaseConnection.get_instance()
        db.write("UPDATE blobs SET status = 'uploaded' WHERE blob_id = %s", (blob_id,))
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_data", methods=["GET"])
@auth_required
def get_data():
    try:
        user_id = session["user_id"]
        container_name = request.args.get("container")
        blob_name = request.args.get("blob")
        db = DatabaseConnection.get_instance()
        blob = db.read_one(
            "SELECT b.blob_id, c.name, b.blob_name, b.blob_size, b.status FROM blobs b JOIN containers c ON b.container_id = c.id WHERE c.name = %s AND c.user_id=%s AND b.blob_name = %s",
            (container_name, user_id, blob_name),
        )
        if not blob:
            return jsonify({"error": "Blob not found"}), 404
        blob_id, container_name, blob_name, blob_size, status = blob
        chunks = db.read_all(
            "SELECT chunk_id, chunk_size, primary_node, replicas FROM chunks WHERE blob_id = %s",
            (blob_id,),
        )
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


@app.route("/delete_data", methods=["DELETE"])
@auth_required
def delete_data():
    try:
        data = request.args
        container_name = data.get("container")
        blob_name = data.get("blob")
        user_id = session["user_id"]

        if not container_name or not blob_name:
            return jsonify({"error": "container_name and blob_name are required"}), 400
        db = DatabaseConnection.get_instance()
        container_id = db.read_one(
            "SELECT id FROM containers WHERE name = %s AND user_id = %s",
            (container_name, user_id),
        )
        db.write(
            "UPDATE blobs SET status = 'deleted' WHERE container_id = %s AND blob_name = %s AND user_id = %s",
            (container_id, blob_name, user_id),
        )
        return jsonify({"status": "success"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/list_blobs", methods=["GET"])
@auth_required
def list_blobs():
    try:
        user_id = session["user_id"]
        container_name = request.args.get("container")
        db = DatabaseConnection.get_instance()
        container_id = db.read_one(
            "SELECT id FROM containers WHERE name = %s AND user_id = %s AND status != 'deleted'",
            (container_name, user_id),
        )
        blobs = db.read_all(
            "SELECT blob_id, blob_name, blob_size FROM blobs WHERE container_id = %s AND user_id = %s AND status != 'deleted'",
            (container_id, user_id),
        )
        if not blobs:
            return jsonify({"blobs": []}), 200
        blobs = [
            {
                "blob_id": blob[0],
                "container_name": container_name,
                "blob_name": blob[1],
                "blob_size": blob[2],
            }
            for blob in blobs
        ]
        return jsonify({"blobs": blobs}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/delete_container", methods=["DELETE"])
@auth_required
def delete_container():

    try:
        data = request.args
        container_name = data.get("container_name")  # Use get to avoid KeyError

        if not container_name:
            return jsonify({"error": "container_name is required"}), 400
        db = DatabaseConnection.get_instance()
        chunks = db.write(
            """
                    WITH container_id AS (
                        SELECT id FROM containers WHERE name = %s
                    ),
                    update_container AS (
                        UPDATE containers
                        SET status = 'deleted'
                        WHERE id = (SELECT id FROM container_id)
                        RETURNING id
                    ),
                    update_blobs AS (
                        UPDATE blobs
                        SET status = 'deleted'
                        WHERE container_id = (SELECT id FROM update_container)
                        RETURNING blob_id
                    ),
                    update_chunks AS (
                    UPDATE chunks
                    SET status = 'deleted'
                    WHERE blob_id IN (SELECT blob_id FROM update_blobs)
                    RETURNING blob_id, chunk_id, primary_node, replicas
                    )
                    SELECT * FROM update_chunks;
                    """,
            (container_name,),
        )

        chunks = [
            {
                "blob_id": chunk[0],
                "chunk_id": chunk[1],
                "primary_node": chunk[2],
                "replicas": chunk[3],
            }
            for chunk in chunks
        ]

        return jsonify({"status": "success", "chunks": chunks}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/list_containers", methods=["GET"])
@auth_required
def list_containers():

    try:
        user_id = session["user_id"]
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        db = DatabaseConnection.get_instance()
        containers = db.read_all(
            "SELECT * FROM containers WHERE status != 'deleted' AND user_id = %s",
            (user_id,),
        )

        if not containers:
            return jsonify({"containers": []}), 200
        containers = [
            {
                "id": container[0],
                "name": container[1],
                "user_id": container[2],
                "status": container[3],
            }
            for container in containers
        ]
        return jsonify({"containers": containers}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("starting manager2")
    # heartbeat = Heartbeat()
    # heartbeat.start()
    app.run(host="0.0.0.0", port=8090)
