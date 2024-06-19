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

export async function createContainer() {
  try {
    const containerName = prompt("Enter a container name:");
    if (!containerName) {
      return;
    }
    const res = await api.createContainerApi(containerName);
    await fetchAndPopulateContainers();
  } catch (error) {
    console.error(error);
  }
}
