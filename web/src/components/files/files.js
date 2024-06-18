import { readFileData, CHUNK_SIZE } from "../../js/utils.js";
import api from "../../js/api.js";

const containerElement = document.getElementById("container");
export async function uploadFile() {
  console.log("upload file");
  const containerName = containerElement.value;
  console.log("containerName", containerName);
  if (!containerName) {
    alert("Please select a container.");
    return;
  }
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  console.log("file", file);
  if (!file) {
    alert("Please select a file.");
    return;
  }

  // Read the file data
  const fileData = await readFileData(file);
  console.log("fileData", fileData);
  await api.uploadFileApi(file, fileData, containerName, CHUNK_SIZE);
  document.getElementById("status").textContent = "Upload complete!";
}
