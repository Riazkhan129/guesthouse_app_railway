import axios from "axios";

// ✅ Detect environment
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "https://ghmsbackend-production.up.railway.app"; // 🔧 UPDATED: fallback added
// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// ✅ Create Axios instance
const API = axios.create({
  baseURL: API_BASE_URL,
});

// ✅ Intercept requests to inject client_id into URL
API.interceptors.request.use((config) => {
  const clientId = localStorage.getItem("client_id"); // ✅ Assumes client_id is stored after login

  const isAuthRoute = config.url?.startsWith("/token");
  const isAbsolute = config.url?.startsWith("http");

  if (clientId && !isAuthRoute && !isAbsolute) {
    // ✅ Send client_id as a custom header instead of rewriting the URL
    config.headers = {
      ...config.headers,
      "X-Client-ID": clientId, // ✅ Backend can read this to filter tenant data
    };
  }

  return config;
});

export default API;
