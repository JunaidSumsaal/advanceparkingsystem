import api from './api';
import { User } from '../types/User';
import { AUTH, ADMIN } from './constants';

interface Credentials {
  email: string;
  password: string;
}

export const login = async ({ email, password }: Partial<Credentials>) => {
  const res = await api.post(`${AUTH}/login`, { email, password });
  return res.data;
};

export const register = async (userData: Partial<User> & { password: string }) => {
  const res = await api.post(`${AUTH}/register`, userData);
  return res.data;
};

export const getMe = async () => {
  const res = await api.get(`${AUTH}/me`);
  return res.data; // User data
};

export const updateProfile = async (updateData: Partial<User> & { password?: string }) => {
  const res = await api.put(`${AUTH}/update`, updateData);
  return res.data;
};

export const forgotPassword = async (email: string) => {
  const res = await api.post(`${AUTH}/forgot-password`, { email });
  return res.data;
};

export const resetPassword = async (resetToken: string, newPassword: string) => {
  const res = await api.post(`${AUTH}/reset-password`, { resetToken, newPassword });
  return res.data;
};

export const logout = async () => {
  const res = await api.post(`${AUTH}/logout`);
  return res.data;
};

export const refreshToken = async (refreshToken: string) => {
  const res = await api.post(`${AUTH}/refresh-token`, { refreshToken });
  return res.data;
};

export const getUsers = async ({ page, limit}:{ page: any, limit: any }) => {
  const res = await api.get(`${ADMIN}/users`, {
    params: { page, limit }
  });
  return res.data;
};

