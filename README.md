# In-House Blob Store

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Components](#components)
- [Setup and Installation](#setup-and-installation)
- [API Endpoints](#api-endpoints)
- [Monitoring](#monitoring)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project implements an in-house blob store service that allows users to store, retrieve, and manage blob data. It supports user authentication, container management, and blob data operations such as upload, download, and deletion.

## Features

- **User Authentication and Authorization**
- **Container Management**: Create, delete, and list containers.
- **Blob Management**: Upload, download, list, and delete blobs.
- **High Availability**
- **Durability**
- **Scalability**
- **Consistency and Reliability**
- **Monitoring with Prometheus**

## Architecture

The architecture is designed to ensure high availability, durability, and scalability. It consists of several components:

- **Client**: Interacts with the blob store service.
- **Load Balancer**: Distributes incoming requests to front-end servers.
- **Front-End Servers**: Handle user requests and forward them to appropriate storage servers.
- **Manager Node**: Manages data nodes, stores metadata, and handles user authentication and authorization.
- **Data Nodes**: Store actual blob data, divided into chunks.
- **Metadata Storage**: Distributed database storing metadata about accounts, containers, and blobs.
- **Monitoring**: Prometheus for monitoring the health and performance of the system.

## Components

### Load Balancer

- **nginx.conf**: Configuration file for Nginx load balancer.

### Front-End Server

- **app.py**: Handles user requests and forwards them to the manager node.
- **Dockerfile**: Dockerfile to build the front-end server image.
- **requirements.txt**: Python dependencies for the front-end server.

### Manager Node

- **app.py**: Manages data nodes, handles metadata, and user authentication.
- **heartbeat.py**: Handles heartbeat signals from data nodes.
- **Dockerfile**: Dockerfile to build the manager node image.
- **requirements.txt**: Python dependencies for the manager node.

### Data Node

- **app.py**: Stores and manages blob data.
- **chunk_manager.py**: Manages blob chunks on data nodes.
- **Dockerfile**: Dockerfile to build the data node image.
- **requirements.txt**: Python dependencies for the data node.

### Metadata Storage

- **init.sql**: SQL script to initialize the metadata database.

### Monitoring

- **prometheus.yml**: Configuration file for Prometheus.

### Client

- **client.py**: Client script to interact with the blob store service.
- **Dockerfile**: Dockerfile to build the client image.
- **requirements.txt**: Python dependencies for the client.

## Setup and Installation

### Prerequisites

- Docker
- Docker Compose

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/blobstore.git
   cd blobstore
   ```

2. Build and start the services:

   ```bash
   docker-compose up --build
   ```

3. Verify that all services are running:

   ```bash
   docker-compose ps
   ```

## API Endpoints

### Authentication

- `POST /auth`: Authenticate a user.

### Containers

- `POST /create_container`: Create a new container.
- `DELETE /delete_container`: Delete a container.
- `GET /list_containers`: List all containers.

### Blobs

- `POST /put_data`: Upload a blob to a container.
- `GET /get_data`: Retrieve a blob from a container.
- `DELETE /delete_data`: Delete a blob from a container.
- `GET /list_blobs`: List all blobs in a container.

## Monitoring

Prometheus is used for monitoring the health and performance of the system.

- Prometheus UI: [http://localhost:9090](http://localhost:9090)

### Configuration

The Prometheus configuration file `prometheus.yml` is located in the `monitoring` directory.

## Contributing

We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) before making a contribution.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
