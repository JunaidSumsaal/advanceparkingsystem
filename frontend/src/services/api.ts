import axios from 'axios';
import Cookies from 'js-cookie';
import { API } from './constants'

const api = axios.create({
  baseURL: API,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refresh = Cookies.get('refresh');
        if (!refresh) {
          throw new Error('No refresh token');
        }

        const res = await axios.post(`${import.meta.env.VITE_API_HOST}/accounts/refresh`, { refresh });
        const { access } = res.data;

        localStorage.setItem('token', access);
        originalRequest.headers['Authorization'] = `Bearer ${access}`;

        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('token');
        Cookies.remove('refresh');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
