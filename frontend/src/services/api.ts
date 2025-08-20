import axios from "axios";
import Cookies from "js-cookie";
import { API, SECURE } from "./constants";

const api = axios.create({
  baseURL: API,
  headers: {
    "Content-Type": "application/json",
  },
});

const setCookie = (key: string, value: string) => {
  Cookies.set(key, value, {
    secure: SECURE === "true" || SECURE === true,
    sameSite: "Strict",
  });
};

api.interceptors.request.use(
  (config) => {
    const token = Cookies.get("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        const refresh = Cookies.get("refresh");

        if (!refresh) {
          return Promise.reject(error);
        }

        const res = await axios.post(`${API}/accounts/refresh/`, {
          refresh,
        });

        const { access, refresh: newRefresh } = res.data;

        setCookie("token", access);
        if (newRefresh) {
          setCookie("refresh", newRefresh);
        }

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (err) {
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
