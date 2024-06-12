const BASE_URL = "http://localhost:8080";
const CHUNK_SIZE = 1 * 1024 * 1024; // 1 MB

const containerElement = document.getElementById("container");
const createContainerBtn = document.getElementById("create-container");

const userId = 1;

document.addEventListener("DOMContentLoaded", async () => {
  await fetchAndPopulateContainers();
  createContainerBtn.addEventListener("click", async () => {
    await createContainer();
  });
});

async function fetchAndPopulateContainers() {
  const containers = await listContainers();
  populateContainers(containers.containers);
}

function populateContainers(containers) {
  containers.forEach((container) => {
    const option = document.createElement("option");
    option.value = container.name;
    option.textContent = container.name;
    containerElement.appendChild(option);
  });
}

async function createContainer() {
  const containerName = prompt("Enter a container name:");
  console.log(containerName);
  if (!containerName) {
    return;
  }
  await createContainerApi(containerName);
}

//apis
async function listContainers() {
  try {
    const response = await fetch(`${BASE_URL}/list_containers?user_id=1`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const containers = await response.json();
    console.log(containers); // Output the list of containers to the console
    return containers;
  } catch (error) {
    console.error("Error fetching containers:", error); // Handle any errors
    throw error;
  }
}

async function createContainerApi(containerName) {
  const response = await fetch("http://localhost:8080/create_container", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: userId,
      container_name: containerName,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }

  await response.json();
  window.location.reload();
}

function readFileData(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      resolve(event.target.result);
    };
    reader.onerror = (error) => {
      reject(error);
    };
    reader.readAsArrayBuffer(file);
  });
}

async function uploadFile() {
  console.log("upload file");
  const containerName = containerElement.value;
  if (!containerName) {
    alert("Please select a container.");
    return;
  }
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a file.");
    return;
  }

  // Read the file data
  const fileData = await readFileData(file);
  console.log("file", fileData);

  const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
  const uploadIdResponse = await fetch(`${BASE_URL}/initiate-upload`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      file_name: file.name,
      file_size: file.size,
      user_id: userId,
      container_name: containerName,
      chunk_size: CHUNK_SIZE,
    }),
  });
  const { blob_id: uploadId, chunk_info: chunkInfo } =
    await uploadIdResponse.json();

  const promises = [];
  for (let i = 0; i < totalChunks; i++) {
    const start = i * CHUNK_SIZE;
    const end = Math.min(file.size, start + CHUNK_SIZE);
    const chunk = fileData.slice(start, end);
    console.log("chunk", chunk);

    const formData = new FormData();
    formData.append("file", chunk);
    formData.append("upload_id", uploadId);
    formData.append("part_number", i + 1);
    formData.append("data_node", chunkInfo[i].data_node);

    promises.push(
      fetch(`${BASE_URL}/upload-part`, {
        method: "POST",
        body: formData,
      })
    );
  }

  const responses = await Promise.all(promises);
  const parts = await Promise.all(responses.map((res) => res.json()));
  console.log(parts);

  await fetch(`${BASE_URL}/complete-upload`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ blob_id: uploadId }),
  });

  document.getElementById("status").textContent = "Upload complete!";
}
