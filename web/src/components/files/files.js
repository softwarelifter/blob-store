import { readFileData, CHUNK_SIZE, ONE_MB } from "../../js/utils.js";
import api from "../../js/api.js";

const containerElement = document.getElementById("container");
export async function uploadFile() {
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
  await api.uploadFileApi(file, fileData, containerName, CHUNK_SIZE);
  document.getElementById("status").textContent = "Upload complete!";
  await createFilesTable();
}

export async function createFilesTable() {
  console.log("create files table");
  const containerName = containerElement.value;
  if (!containerName) {
    alert("Please select a container.");
    return;
  }
  const files = await api.fetchFiles(containerName);
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
    fileSizeTd.textContent =
      Math.round((file.blob_size * 100) / ONE_MB) / 100 + " MB";
    fileCreatedTd.textContent = new Date().toLocaleString();
    tr.appendChild(fileNameTd);
    tr.appendChild(fileSizeTd);
    tr.appendChild(fileCreatedTd);
    tr.appendChild(fileDownloadBtnTd);
    tr.appendChild(fileDeleteBtnTd);
    filesList.appendChild(tr);
  });
}
