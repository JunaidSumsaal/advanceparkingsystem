import api from './api';
import type { User, Credentials } from '../types/User';
import { AUTH, ADMIN } from './constants';
import apiHelper from '../utils/apiHelper';


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

// Profile (get current user)
export const getMe = async () => {
  const res = await apiHelper.get(`${AUTH}/profile/`);
  return {profile: res.data};
};

// Update profile (same endpoint, usually PUT or PATCH)
export const updateProfile = async (updateData: Partial<User>) => {
  const res = await apiHelper.put(`${AUTH}/profile/`, updateData);
  return res.data;
};

// Change password
export const changePassword = async (oldPassword: string, newPassword: string) => {
  const res = await apiHelper.post(`${AUTH}/change-password/`, { oldPassword, newPassword });
  return res.data;
};

// Logout
export const logout = async () => {
  const res = await apiHelper.post(`${AUTH}/logout/`);
  return res.data;
};

// Refresh token
export const refresh = async (refresh: string) => {
  const res = await apiHelper.post(`${AUTH}/refresh/`, { refresh });
  return res.data;
};

// Admin: list users
export const getUsers = async ({ page, limit }: { page: number; limit: number }) => {
  const res = await apiHelper.get(`${ADMIN}/users/`, {
    params: { page, limit },
  });
  return { users: res.data };
};
