// apiClient.js
import login from "../components/login/login";

const BASE_URL = "http://localhost:8080";
const commonHeaders = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${document.cookie.split("=")[1]}`,
};

class ApiClient {
  constructor(baseURL = BASE_URL, defaultHeaders = commonHeaders) {
    this.baseURL = baseURL;
    this.defaultHeaders = defaultHeaders;
  }

  // Method to handle GET requests
  get(endpoint, customHeaders = {}) {
    return this.request(endpoint, "GET", null, customHeaders);
  }

  // Method to handle POST requests
  post(endpoint, body, customHeaders = {}) {
    return this.request(endpoint, "POST", body, customHeaders);
  }

  // Method to handle PUT requests
  put(endpoint, body, customHeaders = {}) {
    return this.request(endpoint, "PUT", body, customHeaders);
  }

  // Method to handle DELETE requests
  delete(endpoint, customHeaders = {}) {
    return this.request(endpoint, "DELETE", null, customHeaders);
  }

  // Core request method
  async request(endpoint, method, body = null, customHeaders = {}) {
    const headers = { ...this.defaultHeaders, ...customHeaders };

    const options = {
      method,
      headers,
    };

    if (body) {
      if (body instanceof FormData) {
        delete headers["Content-Type"]; // Let the browser set it automatically
        options.body = body;
      } else {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
      }
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, options);

    return this.handleResponse(response);
  }

  // Handle the response
  async handleResponse(response) {
    if (!response.ok) {
      if (response.status === 401) {
        login.handleLogin();
      }
      const error = await response.json();
      throw new Error(error.message || "API request failed");
    }
    return await response.json();
  }
}

export default new ApiClient();
