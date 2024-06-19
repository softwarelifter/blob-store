import api from "../../js/api.js";

const containerElement = document.getElementById("container");

export async function fetchAndPopulateContainers() {
  try {
    const containers = await api.listContainers();
    containers.containers.forEach((container) => {
      const option = document.createElement("option");
      option.value = container.name;
      option.textContent = container.name;
      containerElement.appendChild(option);
    });
  } catch (error) {
    console.error(error);
  }
}

function appendContainer(container) {
  const option = document.createElement("option");
  option.selected = true;
  option.value = container;
  option.textContent = container;
  containerElement.appendChild(option);
}

export async function createContainer() {
  try {
    const containerName = prompt("Enter a container name:");
    if (!containerName) {
      return;
    }
    const res = await api.createContainerApi(containerName);
    appendContainer(containerName);
  } catch (error) {
    console.error(error);
  }
}

export async function deleteContainer() {
  try {
    const containerName = containerElement.value;
    if (!containerName) {
      alert("Please select a container to delete");
      return;
    }
    await api.deleteContainerApi(containerName);
    document.getElementById(
      "status"
    ).textContent = `deleted container ${containerName}!`;
    location.reload();
  } catch (error) {
    console.error(error);
  }
}
