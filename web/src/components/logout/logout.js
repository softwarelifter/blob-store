import api from "../../js/api.js";
import { handleLoginRedirect } from "../../js/utils.js";

class Logout {
  async handleLogout(e) {
    e.preventDefault();
    await api.logout();
    document.cookie = "authToken=";
    handleLoginRedirect();
  }
}

export default new Logout();
