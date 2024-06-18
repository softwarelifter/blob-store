import api from "./api";
import login from "../components/login/login";
import logout from "../components/logout/logout";
import {
  fetchAndPopulateContainers,
  createContainer,
} from "../components/containers/containers";
import { uploadFile, createFilesTable } from "../components/files/files";

import "../styles/styles.css";

document
  .getElementById("logout")
  .addEventListener("click", logout.handleLogout);
document
  .getElementById("create-container")
  .addEventListener("click", createContainer);
document.getElementById("upload-file").addEventListener("click", uploadFile);
document
  .getElementById("container")
  .addEventListener("change", createFilesTable);
await login.isLoggedIn();

await fetchAndPopulateContainers();
await createFilesTable();

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

// async function listContainers() {
//   try {
//     const response = await fetch(`${BASE_URL}/list_containers?user_id=1`);
//     if (!response.ok) {
//       throw new Error(`HTTP error! Status: ${response.status}`);
//     }
//     const containers = await response.json();
//     console.log(containers); // Output the list of containers to the console
//     return containers;
//   } catch (error) {
//     console.error("Error fetching containers:", error); // Handle any errors
//     throw error;
//   }
// }

// async function createContainerApi(containerName) {
//   const response = await fetch("http://localhost:8080/create_container", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({
//       user_id: userId,
//       container_name: containerName,
//     }),
//   });

//   if (!response.ok) {
//     throw new Error(`HTTP error! Status: ${response.status}`);
//   }

//   await response.json();
//   window.location.reload();
// }

// function readFileData(file) {
//   return new Promise((resolve, reject) => {
//     const reader = new FileReader();
//     reader.onload = (event) => {
//       resolve(event.target.result);
//     };
//     reader.onerror = (error) => {
//       reject(error);
//     };
//     reader.readAsArrayBuffer(file);
//   });
// }

// async function uploadFile() {
//   console.log("upload file");
//   const containerName = containerElement.value;
//   if (!containerName) {
//     alert("Please select a container.");
//     return;
//   }
//   const fileInput = document.getElementById("fileInput");
//   const file = fileInput.files[0];
//   if (!file) {
//     alert("Please select a file.");
//     return;
//   }

//   // Read the file data
//   const fileData = await readFileData(file);
//   await api.uploadFileApi(file, fileData, containerName, CHUNK_SIZE);
//   document.getElementById("status").textContent = "Upload complete!";
// }

async function reconstructFile(json, outputFileName) {
  let byteArrays = [];

  for (const chunkId in json) {
    if (json.hasOwnProperty(chunkId)) {
      const base64Chunk = json[chunkId].blob_data;
      const byteCharacters = atob(base64Chunk);
      const byteNumbers = new Array(byteCharacters.length);

      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }

      const byteArray = new Uint8Array(byteNumbers);
      byteArrays.push(byteArray);
    }
  }

  const blob = new Blob(byteArrays, { type: "application/octet-stream" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = outputFileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function downloadFile(row) {
  const containerName = containerElement.value;
  const fileName = row.children[0].textContent;

  try {
    response = await api.downloadFileApi(fileName, containerName);
    await reconstructFile(response, fileName);
  } catch (error) {
    console.error("Error:", error);
  }
}

// async function streamDownloadFile(row) {
//   const containerName = containerElement.value;
//   const fileName = row.children[0].textContent;
//   console.log("download file", fileName);
//   if (!containerName) {
//     alert("Please select a container.");
//     return;
//   }

//   const response = await fetch(
//     `${BASE_URL}/get_data?user_id=${userId}&container=${containerName}&blob=${fileName}`
//   );
//   if (!response.ok) {
//     throw new Error(`HTTP error! Status: ${response.status}`);
//   }
//   const contentType = response.headers.get("Content-Type");
//   console.log("Content-Type:", contentType);
//   const data = await response.json();
//   console.log(data);

//   chunks = Object.values(data).forEach((chunk) => chunk.blob_data);

//   // const blob = await response.blob();
//   // console.log(blob);
//   const url = URL.createObjectURL(new Blob(chunks, { type: contentType }));
//   const a = document.createElement("a");
//   a.href = url;
//   a.download = fileName;
//   a.click();
//   URL.revokeObjectURL(url);
// }

async function deleteFile(row) {
  const containerName = containerElement.value;
  const fileName = row.children[0].textContent;
  console.log("delete file", fileName);
  await api.deleteFileApi(fileName, containerName);
  // await fetchFiles();
}
