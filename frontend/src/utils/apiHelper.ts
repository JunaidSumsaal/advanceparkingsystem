/* eslint-disable @typescript-eslint/no-explicit-any */
import Cookies from 'js-cookie';
import api from '../services/api';

const apiHelper = {
  get: async (url: string, config: object = {}) => {
    try {
      const response = await api.get(url, {
        ...config,
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
          ...(config as any).headers,
        },
      });
      return response.data;
    } catch (error) {
      console.error("API GET error:", error);
      throw error;
    }
  },

  post: async (url: string, data?: object, config: object = {}) => {
    try {
      const response = await api.post(url, data, {
        ...config,
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
          ...(config as any).headers,
        },
      });
      return response.data;
    } catch (error) {
      console.error("API POST error:", error);
      throw error;
    }
  },

  put: async (url: string, data: object, config: object = {}) => {
    try {
      const response = await api.put(url, data, {
        ...config,
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
          ...(config as any).headers,
        },
      });
      return response.data;
    } catch (error) {
      console.error("API PUT error:", error);
      throw error;
    }
  },

  patch: async (url: string, data: object, config: object = {}) => {
    try {
      const response = await api.patch(url, data, {
        ...config,
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
          ...(config as any).headers,
        },
      });
      return response.data;
    } catch (error) {
      console.error("API PATCH error:", error);
      throw error;
    }
  },

  delete: async (url: string, config: object = {}) => {
    try {
      const response = await api.delete(url, {
        ...config,
        headers: {
          Authorization: `Bearer ${Cookies.get('token')}`,
          ...(config as any).headers,
        },
      });
      return response.data;
    } catch (error) {
      console.error("API DELETE error:", error);
      throw error;
    }
  },
};

export default apiHelper;
