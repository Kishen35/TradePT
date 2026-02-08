export class ApiHelper {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  /* =========================
     Internal request handler
     ========================= */
  async request(
    path,
    {
      method = "GET",
      headers = {},
      body = null,
      credentials = "include", // useful for cookies / sessions
    } = {},
  ) {
    const config = {
      method,
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      credentials,
    };

    if (body) {
      config.body = JSON.stringify(body);
    }

    const response = await fetch(`${this.baseUrl}${path}`, config);

    let data;
    const contentType = response.headers.get("content-type");

    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      throw new Error(
        data?.detail || data?.message || `HTTP ${response.status}`,
      );
    }

    return data;
  }

  /* =========================
     Public HTTP methods
     ========================= */
  get(path, options = {}) {
    return this.request(path, { ...options, method: "GET" });
  }

  post(path, body, options = {}) {
    return this.request(path, { ...options, method: "POST", body });
  }

  put(path, body, options = {}) {
    return this.request(path, { ...options, method: "PUT", body });
  }

  delete(path, options = {}) {
    return this.request(path, { ...options, method: "DELETE" });
  }

  /* =========================
     Example API calls
     ========================= */

  listUsers() {
    return this.get("/users");
  }

  login(payload) {
    return this.post("/users/login", payload);
  }

  register(payload) {
    return this.post("/users", payload);
  }
}

export const apiHelper = new ApiHelper();
