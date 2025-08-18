import React, { useState, useEffect, useCallback, createContext, useContext } from 'react';
import Cookies from 'js-cookie';
import { getMe, refresh, logout as apiLogout } from '../services/authService';
import type { User } from '../types/User';
import type { AuthContextType } from '../types/context/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /** 🔑 Login */
  const login = (access: string, refreshToken: string) => {
    Cookies.set('token', access);
    Cookies.set('refresh', refreshToken);
    fetchUser(); // immediately load profile
  };

  /** 🚪 Logout */
  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch (err) {
      console.error('Logout failed', err);
    }
    Cookies.remove('refresh');
    Cookies.remove('token');
    setUser(null);
  }, []);

  /** ♻️ Refresh token */
  const refreshAccessToken = useCallback(async () => {
    try {
      const data = await refresh(Cookies.get('refresh') || '');
      const { access, refresh: newRefresh } = data;
      Cookies.set('token', access);
      Cookies.set('refresh', newRefresh);
    } catch (err) {
      console.error('Error refreshing token', err);
      logout();
    }
  }, [logout]);

  /** 👤 Fetch current user */
  const fetchUser = useCallback(async () => {
  try {
    const user = await getMe()
    setUser(user);
    setError(null);
  } catch (err) {
    console.error("Error fetching user", err);
    setError("Failed to fetch user");
  } finally {
    setLoading(false);
  }
}, []);


  /** On mount */
  useEffect(() => {
    if (Cookies.get('token')) {
      fetchUser().catch(() => refreshAccessToken());
    } else {
      setLoading(false);
    }
  }, [fetchUser, refreshAccessToken]);

  /** Auto refresh token every 14min */
  useEffect(() => {
    const interval = setInterval(() => {
      refreshAccessToken();
    }, 1000 * 60 * 14);
    return () => clearInterval(interval);
  }, [refreshAccessToken]);

  return (
    <AuthContext.Provider
      value={{ user, login, logout, refreshAccessToken, loading, error }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuthContext = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuthContext must be used within AuthProvider');
  }
  return ctx;
};
