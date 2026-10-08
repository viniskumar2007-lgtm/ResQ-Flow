const API_BASE_URL = "http://10.250.167.191:8000";

// Backend integration mode
// false = use the real FastAPI backend
export const DEMO_MODE = false;

export const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  let data = null;

  try {
    data = await response.json();
  } catch {
    // Response did not contain JSON
  }

  if (!response.ok) {
    const rawMessage =
      data?.detail ||
      data?.message ||
      `Request failed (${response.status})`;

    const message =
      typeof rawMessage === "string"
        ? rawMessage
        : JSON.stringify(rawMessage);

    throw new Error(message);
  }

  return data;
};

export { API_BASE_URL };