import apiClient from "./apiClient";

class Api {
  async isLoggedIn() {
    return await apiClient.get("/is-logged-in");
  }
  async signIn(formData) {
    return await apiClient.post("/login", {
      email: formData.get("email"),
      password: formData.get("password"),
      username: formData.get("username"),
    });
  }

  async signUp(formData) {
    return await apiClient.post("/signup", {
      email: formData.get("email"),
      password: formData.get("password"),
      username: formData.get("username"),
    });
  }

  async logout() {
    return await apiClient.post("/logout");
  }

  async listContainers() {
    return await apiClient.get("/list_containers");
  }

  async createContainerApi(containerName) {
    return await apiClient.post("/create_container", {
      container_name: containerName,
    });
  }
  async uploadFileApi(file, fileData, containerName, chunkSize) {
    const totalChunks = Math.ceil(file.size / chunkSize);

    const payload = {
      file_name: file.name,
      file_size: file.size,
      container_name: containerName,
      chunk_size: chunkSize,
    };

    const uploadIdResponse = await apiClient.post("/initiate-upload", payload);
    const { blob_id: uploadId, chunk_info: chunkInfo } = await uploadIdResponse;
    console.log("uploadId", uploadId);

    const promises = [];
    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(file.size, start + chunkSize);
      const chunk = fileData.slice(start, end);
      console.log("chunk", chunk);

      const formData = new FormData();
      formData.append("file", new Blob([chunk]));
      formData.append("upload_id", uploadId);
      formData.append("part_number", i);
      formData.append("data_node", chunkInfo[i].data_node);

      const uploadPartPromise = await apiClient.post("/upload-part", formData);
      // promises.push(apiClient.post("/upload-part", formData));
      // const uploadPartPromise = fetch("http://localhost:8080/upload-part", {
      //   method: "POST",
      //   body: formData,
      // }).then((response) => response.json());

      promises.push(uploadPartPromise);
    }

    const responses = await Promise.all(promises);
    // const parts = await Promise.all(responses.map((res) => res.json()));
    // console.log(parts);

    await apiClient.post("/complete-upload", { blob_id: uploadId });
  }

  async fetchFiles(containerName) {
    return await apiClient.get(`/list_blobs?container=${containerName}`);
  }

  async downloadFileApi(fileName, containerName) {
    return await apiClient.get(
      `/get_data?container=${containerName}&blob=${fileName}`
    );
  }

  async deleteFileApi(fileName, containerName) {
    if (!containerName) {
      alert("Please select a container.");
      return;
    }
    return await apiClient.delete(
      `/delete-blob?container=${containerName}&blob=${fileName}`
    );
  }
}

export default new Api();
