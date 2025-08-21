import api from './api';
import apiHelper from '../utils/apiHelper';
import { AUTH, ADMIN, NEWSLETTER, NEWSLETTER_SUBSCRIBE } from './constants';
import type { User, Credentials } from '../types/User';

// Login
export const login = async ({ username, password }: Partial<Credentials>) => {
  const res = await api.post(`${AUTH}/login/`, { username, password });
  return res.data;
};

// Register
export const register = async (userData: Partial<User> & { password: string }) => {
  const res = await api.post(`${AUTH}/register/`, userData);
  return res.data;
};

// Profile
export const getMe = async () => {
  const res = await apiHelper.get(`${AUTH}/profile/`);
  return res;
};

export const updateProfile = async (updateData: Partial<User>) => {
  const res = await apiHelper.put(`${AUTH}/profile/`, updateData);
  return res;
};

// Change Password
export const changePassword = async (oldPassword: string, newPassword: string) => {
  const res = await apiHelper.post(`${AUTH}/change-password/`, { oldPassword, newPassword });
  return res;
};

// Logout
export const logout = async () => {
  const res = await apiHelper.post(`${AUTH}/logout/`);
  return res;
};

// Refresh Token
export const refresh = async (refresh: string) => {
  const res = await apiHelper.post(`${AUTH}/refresh/`, { refresh });
  return res;
};

// Admin Users
export const getAdminUsers = async ({ page = 1, limit = 20 }) => {
  const res = await apiHelper.get(`${AUTH}${ADMIN}/users/`, { params: { page, limit } });
  return res;
};

export const getAdminUser = async (id: number) => {
  const res = await apiHelper.get(`${AUTH}${ADMIN}/users/${id}/`);
  return res;
};

export const addAttendant = async (data: { username: string; email: string; password: string; facility: number }) => {
  const res = await apiHelper.post(`${AUTH}${ADMIN}/users/add-attendant/`, data);
  return res;
};

// Newsletter
export const getNewsletter = async () => {
  const res = await apiHelper.get(`${AUTH}${NEWSLETTER}/`);
  return res;
};

export const updateNewsletter = async (data: { subscribed: boolean }) => {
  const res = await apiHelper.patch(`${AUTH}${NEWSLETTER}/`, data);
  return res;
};

export const subscribeNewsletter = async (email: string) => {
  const res = await api.post(`${AUTH}${NEWSLETTER_SUBSCRIBE}/`, { email });
  return res.data;
};
