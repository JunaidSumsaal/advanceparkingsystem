import React, { createContext, useState, useContext, useEffect } from 'react';
import { User } from '../types/User';
import { getMe, getUsers } from '../services/authService';
import { AuthContextType } from '../types/context/auth';
import Cookies from 'js-cookie';
import axios from 'axios';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [totalUsers, setTotalUsers] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);

  const refreshAccessToken = async () => {
    const refreshToken = Cookies.get('refreshToken');
    if (!refreshToken) {
      logout();
      return;
    }

    try {
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh-token`, { refreshToken });
      const { accessToken } = res.data;
      localStorage.setItem('token', accessToken);
      setToken(accessToken);
    } catch (error) {
      console.error(error);
      logout();
    }
  };

  const fetchUsers = async () => {
    if (user?.isAdmin) {
      try {
        const { users, totalUsers, totalPages, currentPage: current } = await getUsers({ page: currentPage, limit: 10 });
        setUsers(users);
        setTotalUsers(totalUsers);
        setTotalPages(totalPages);
        setCurrentPage(current);
      } catch (err) {
        console.error("Error fetching users", err);
      }
    }
  };

  useEffect(() => {
    if (token) {
      getMe()
        .then((data: any) => setUser(data))
        .catch(() => refreshAccessToken());
    }
  }, [token]);

  useEffect(() => {
    fetchUsers();
  }, [currentPage, user?.isAdmin]);

  const login = (accessToken: string) => {
    localStorage.setItem('token', accessToken);
    setToken(accessToken);
  };

  const logout = async () => {
    try {
      await axios.post(`${import.meta.env.VITE_API_URL}/auth/logout`, {}, {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });
    } catch (error) {
      console.error('Logout API call failed', error);
    }
    localStorage.removeItem('token');
    Cookies.remove('refreshToken');
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      users,
      token,
      login,
      logout,
      totalUsers,
      currentPage,
      totalPages,
      setCurrentPage
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
