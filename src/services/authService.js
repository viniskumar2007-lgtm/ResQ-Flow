import { apiRequest } from "./api";

export const login = async (username, password) => {
  const data = await apiRequest("/api/auth/login", {
    method: "POST",
   body: JSON.stringify({
  email: username,
  password,
}),
  });

  localStorage.setItem("access_token", data.access_token);

  if (data.refresh_token) {
    localStorage.setItem("refresh_token", data.refresh_token);
  }

  if (data.user) {
    localStorage.setItem("user", JSON.stringify(data.user));
  }

  return data;
};

export const logout = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
};

export const getCurrentUser = () => {
  const user = localStorage.getItem("user");

  if (!user) {
    return null;
  }

  try {
    return JSON.parse(user);
  } catch {
    return null;
  }
};

export const isAuthenticated = () => {
  return Boolean(localStorage.getItem("access_token"));
};