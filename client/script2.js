const BASE_URL = "http://localhost:8080";
const CHUNK_SIZE = 1 * 1024 * 1024; // 1 MB

const containerElement = document.getElementById("container");
const createContainerBtn = document.getElementById("create-container");

const userId = 1;

document.addEventListener("DOMContentLoaded", async () => {
  await fetchAndPopulateContainers();
  await fetchFiles();
  createContainerBtn.addEventListener("click", async () => {
    await createContainer();
  });
  document
    .getElementById("files-list")
    .addEventListener("click", handleFileActions);
});

async function handleFileActions(event) {
  const target = event.target;
  const row = target.closest("tr");
  if (target.tagName === "BUTTON") {
    const action = target.textContent.toLowerCase();
    if (action === "download") {
      await downloadFile(row);
    } else if (action === "delete") {
      await deleteFile(row);
    }
  }
}

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

async function fetchFiles() {
  const containerName = containerElement.value;
  if (!containerName) {
    alert("Please select a container.");
    return;
  }

  const response = await fetch(
    `${BASE_URL}/list_blobs?user_id=${userId}&container=${containerName}`
  );
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }

  const files = await response.json();
  console.log(files);
  const filesList = document.getElementById("files-list");
  filesList.innerHTML = "";
  files.blobs.forEach((file) => {
    const tr = document.createElement("tr");
    const fileNameTd = document.createElement("td");
    const fileSizeTd = document.createElement("td");
    const fileCreatedTd = document.createElement("td");
    const fileDownloadBtnTd = document.createElement("td");
    const fileDeleteBtnTd = document.createElement("td");
    const fileDownloadBtn = document.createElement("button");
    fileDownloadBtn.textContent = "Download";
    const fileDeleteBtn = document.createElement("button");
    fileDeleteBtnTd.appendChild(fileDeleteBtn);
    fileDeleteBtn.textContent = "Delete";
    fileDownloadBtnTd.appendChild(fileDownloadBtn);

    fileNameTd.textContent = file.blob_name;
    fileSizeTd.textContent = file.blob_size;
    fileCreatedTd.textContent = new Date().toLocaleString();
    tr.appendChild(fileNameTd);
    tr.appendChild(fileSizeTd);
    tr.appendChild(fileCreatedTd);
    tr.appendChild(fileDownloadBtnTd);
    tr.appendChild(fileDeleteBtnTd);
    filesList.appendChild(tr);
  });
}

async function downloadFile(row) {
  const containerName = containerElement.value;
  const fileName = row.children[0].textContent;
  console.log("download file", fileName);
  if (!containerName) {
    alert("Please select a container.");
    return;
  }

  const response = await fetch(
    `${BASE_URL}/download?user_id=${userId}&container=${containerName}&blob=${fileName}`
  );
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;
  a.click();
  URL.revokeObjectURL(url);
}

async function deleteFile(row) {
  const containerName = containerElement.value;
  const fileName = row.children[0].textContent;
  console.log("delete file", fileName);
  if (!containerName) {
    alert("Please select a container.");
    return;
  }

  const response = await fetch(
    `${BASE_URL}/delete-blob?user_id=${userId}&container_name=${containerName}&blob_name=${fileName}`,
    {
      method: "DELETE",
    }
  );
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }

  await response.json();
  await fetchFiles();
}
