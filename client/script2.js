const BASE_URL = "http://localhost:8080";

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
