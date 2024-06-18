import api from "./api";
import login from "../components/login/login";
import logout from "../components/logout/logout";
import {
  fetchAndPopulateContainers,
  createContainer,
} from "../components/containers/containers";
import {
  uploadFile,
  createFilesTable,
  handleFileActions,
} from "../components/files/files";

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

document
  .getElementById("files-list")
  .addEventListener("click", handleFileActions);

await login.isLoggedIn();

await fetchAndPopulateContainers();
await createFilesTable();
