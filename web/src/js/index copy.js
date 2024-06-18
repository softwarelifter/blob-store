import api from "./api";
import { readFileData } from "./utils";
import "../styles/styles.css";

const CHUNK_SIZE = 1 * 1024 * 1024; // 1 MB
const ONE_MB = 1024 * 1024;

function addEventListenerOnce(element, event, handler) {
  const listenerAttribute = `data-${event}-listener`;

  if (element && !element.hasAttribute(listenerAttribute)) {
    element.setAttribute(listenerAttribute, true);
    element.addEventListener(event, handler);
  }
}

const containerElement = document.getElementById("container");
const createContainerBtn = document.getElementById("create-container");

addEventListenerOnce(document.getElementById("logout"), "click", logout);

function toggleLoginViews() {
  if (document.getElementById("main-content").classList.contains("hide")) {
    document.getElementById("main-content").classList.remove("hide");
    document.getElementById("login-dialog").classList.add("hide");
  } else if (
    document.getElementById("login-dialog").classList.contains("hide")
  ) {
    document.getElementById("main-content").classList.add("hide");
    document.getElementById("login-dialog").classList.remove("hide");
  }
}

const response = await api.isLoggedIn();

console.log(response);
if (response.error) {
  document.getElementById("main-content").classList.add("hide");
  document.getElementById("login-dialog").classList.remove("hide");
  const loginFormDialog = document.getElementById("loginSignupForm");
  const signupForm = document.getElementById("signupForm");
  const signupLink = document.getElementById("signupLink");
  const loginLink = document.getElementById("loginLink");

  // Show signup form and hide login form
  signupLink.addEventListener("click", function (event) {
    event.preventDefault();
    loginFormDialog.style.display = "none";
    signupForm.style.display = "block";
  });

  // Show login form and hide signup form
  loginLink.addEventListener("click", function (event) {
    event.preventDefault();
    signupForm.style.display = "none";
    loginFormDialog.style.display = "block";
  });

  // Handle login form submission
  addEventListenerOnce(document.getElementById("loginForm"), "submit", signIn);

  // document
  //   .getElementById("loginForm")
  //   .addEventListener("submit", async (e) => {
  //     e.preventDefault();
  //     console.log("login form");
  //   });

  // Handle signup form submission
  document
    .getElementById("signupForm")
    .addEventListener("submit", function (event) {
      event.preventDefault();
      // Get signup form values
      const email = document.getElementById("signupEmail").value;
      const password = document.getElementById("signupPassword").value;
      const confirmPassword = document.getElementById("confirmPassword").value;
    });
} else {
  // await fetchAndPopulateContainers();
  // createFilesTable();
  createContainerBtn.addEventListener("click", async () => {
    await createContainer();
  });
  document
    .getElementById("files-list")
    .addEventListener("click", handleFileActions);
  containerElement.addEventListener("change", async () => {
    console.log("container changed");
    await fetchFiles();
  });
}

function handleDashboardRedirect() {
  // window.location.href = "/dashboard";
  toggleLoginViews();
}

async function signIn(e) {
  e.preventDefault();
  e.stopPropagation();

  const formData = new FormData();
  formData.append("email", document.getElementById("email").value);
  formData.append("password", document.getElementById("password").value);
  formData.append("username", document.getElementById("username").value);
  const responsse = await api.signIn(formData);

  if (responsse.status === "success") {
    alert("Login successful");
    document.cookie = `authToken=${responsse.token}`;
    console.log("document.cookie", document.cookie);
    handleDashboardRedirect();
  } else {
    alert("Invalid credentials");
  }
}
async function signUp(e) {
  e.preventDefault();
  const formData = new FormData(e.target);
  const response = await api.signUp(formData);

  if (response.status === "success") {
    alert("Signup successful");
  } else {
    alert("Invalid credentials");
  }
}

async function logout(e) {
  e.preventDefault();
  console.log("logout");
  await api.logout();
  document.cookie = "authToken=";
  toggleLoginViews();
}

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
  const containers = await api.listContainers();
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
  await api.createContainerApi(containerName);
}

async function createFilesTable() {
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
  await api.uploadFileApi(file, fileData, containerName, CHUNK_SIZE);
  document.getElementById("status").textContent = "Upload complete!";
}

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
