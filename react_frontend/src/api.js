import axios from "axios";

// ✅ Detect environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// ✅ Create Axios instance
const API = axios.create({
  baseURL: API_BASE_URL,
});

// ✅ Intercept requests to inject client_id into URL
API.interceptors.request.use((config) => {
  const clientId = localStorage.getItem("client_id"); // ✅ Assumes client_id is stored after login

  const isAuthRoute = config.url?.startsWith("/token");
  const isAbsolute = config.url?.startsWith("http");

  if (clientId && config.url && !config.url.startsWith("/token")) {
    // ✅ Rewrite URL to include client_id prefix
    config.url = `/${clientId}${config.url}`;
  }

  return config;
});

export default API;
