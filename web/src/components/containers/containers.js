import api from "../../js/api.js";

const containerElement = document.getElementById("container");

export async function fetchAndPopulateContainers() {
  const containers = await api.listContainers();
  containers.containers.forEach((container) => {
    const option = document.createElement("option");
    option.value = container.name;
    option.textContent = container.name;
    containerElement.appendChild(option);
  });
}

export async function createContainer() {
  const containerName = prompt("Enter a container name:");
  console.log(containerName);
  if (!containerName) {
    return;
  }
  const res = await api.createContainerApi(containerName);
  await fetchAndPopulateContainers();
  console.log("res", res);
}
