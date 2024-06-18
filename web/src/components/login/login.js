import api from "../../js/api.js";
import {
  handleDashboardRedirect,
  handleLoginRedirect,
} from "../../js/utils.js";

class Login {
  async isLoggedIn() {
    try {
      const res = await api.isLoggedIn();
      if (res.status === "success") {
        handleDashboardRedirect();
      }
    } catch (e) {
      console.log("Error:", e);
      this.handleLogin();
    }
  }
  async handleLogin() {
    handleLoginRedirect();
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
    document
      .getElementById("loginForm")
      .addEventListener("submit", this.signIn);

    // Handle signup form submission
    document
      .getElementById("signupForm")
      .addEventListener("submit", function (event) {
        event.preventDefault();
        // Get signup form values
        const email = document.getElementById("signupEmail").value;
        const password = document.getElementById("signupPassword").value;
        const confirmPassword =
          document.getElementById("confirmPassword").value;
      });
  }

  async signIn(e) {
    e.preventDefault();

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
  async signUp(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await api.signUp(formData);

    if (response.status === "success") {
      alert("Signup successful");
    } else {
      alert("Invalid credentials");
    }
  }
}

export default new Login();
