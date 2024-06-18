export const CHUNK_SIZE = 1 * 1024 * 1024; // 1 MB
export const ONE_MB = 1024 * 1024;

export function readFileData(file) {
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

export async function reconstructFile(json, outputFileName) {
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
