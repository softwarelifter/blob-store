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

CREATE TABLE blobs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    container_id INTEGER REFERENCES containers(id),
    data BYTEA NOT NULL
);
