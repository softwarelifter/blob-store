CREATE DATABASE blobstore;
CREATE USER blobstore_user WITH ENCRYPTED PASSWORD 'blobstore_password';
GRANT ALL PRIVILEGES ON DATABASE blobstore TO blobstore_user;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE containers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE data_nodes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE blobs (
    id SERIAL PRIMARY KEY,
    blob_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    container_id INTEGER REFERENCES containers(id),
    blob_size INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'uploading'
);

CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL,
    blob_id VARCHAR(255) REFERENCES blobs(blob_id),   
    chunk_size INTEGER NOT NULL,
    primary_node VARCHAR(50) REFERENCES data_nodes(name),
    replicas VARCHAR(50)[] NOT NULL
);
