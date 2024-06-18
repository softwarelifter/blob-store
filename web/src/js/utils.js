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

function addEventListenerOnce(element, event, handler) {
  const listenerAttribute = `data-${event}-listener`;

  if (element && !element.hasAttribute(listenerAttribute)) {
    element.setAttribute(listenerAttribute, true);
    element.addEventListener(event, handler);
  }
}

export function handleDashboardRedirect() {
  document.getElementById("main-content").style.display = "block";
  document.getElementById("login-dialog").style.display = "none";
}

export function handleLoginRedirect() {
  document.getElementById("main-content").style.display = "none";
  document.getElementById("login-dialog").style.display = "block";
}
