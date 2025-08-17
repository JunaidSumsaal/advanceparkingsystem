import React, {
  useState,
  useEffect,
  useCallback,
} from 'react';
import {
  getMe,
  getUsers,
  refresh,
  logout as logouts,
} from '../services/authService';
import type { User } from '../types/User';
import Cookies from 'js-cookie';
import { AuthContext } from './Auth';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /** Logout */
  const logout = useCallback(async () => {
    try {
      await logouts();
    } catch (err) {
      console.error('Logout API call failed', err);
    }
    Cookies.remove('refresh');
    Cookies.remove('token');
    setUser(null);
    setUsers([]);
  }, []);

  /** Refresh access token */
  const refreshAccessToken = useCallback(async () => {
    try {
      const res = await refresh(Cookies.get('refresh') || '');
      const { access, refresh: newRefresh } = res.data;

      Cookies.set('refresh', newRefresh);
      Cookies.set('token', access);
    } catch (err) {
      console.error('Error refreshing token', err);
      logout();
    }
  }, [logout]);

  /** Fetch logged-in user profile */
  const fetchUser = useCallback(async () => {
    try {
      const { profile } = await getMe();
      setUser(profile);
      setError(null);
    } catch (err) {
      console.error('Error fetching user', err);
      setError('Failed to fetch user');
    } finally {
      setLoading(false);
    }
  }, []);

  /** Fetch all users (only for admin) */
  const fetchUsers = useCallback(async () => {
    if (user?.role === 'admin') {
      try {
        const { users } = await getUsers({
          page: currentPage,
          limit: 10,
        });
        setUsers(users);
      } catch (err) {
        console.error('Error fetching users', err);
        setError('Failed to fetch users');
      }
    }
  }, [user?.role, currentPage]);

  /** On mount: check token and fetch profile */
  useEffect(() => {
    if (Cookies.get('token')) {
      getMe()
        .then(({ profile }) => {
          setUser(profile);
          setError(null);
        })
        .catch(() => refreshAccessToken())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [refreshAccessToken]);

  /** Fetch users when role or page changes */
  useEffect(() => {
    if (user?.role === 'admin') {
      fetchUsers();
    }
  }, [user?.role, currentPage, fetchUsers]);

  /** Auto-refresh token every 14 mins */
  useEffect(() => {
    const interval = setInterval(() => {
      refreshAccessToken();
    }, 1000 * 60 * 14); // ~14 minutes

    return () => clearInterval(interval);
  }, [refreshAccessToken]);

  /** Login */
  const login = (access: string, refresh: string) => {
    Cookies.set('token', access);
    Cookies.set('refresh', refresh);
    fetchUser(); // fetch profile immediately after login
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        users,
        login,
        logout,
        refreshAccessToken,
        loading,
        error,
        currentPage,
        setCurrentPage,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

