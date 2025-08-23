import React, {
  useState,
  useEffect,
  useCallback,
  createContext,
  useContext,
} from "react";
import Cookies from "js-cookie";
import {
  getMe,
  refresh,
  logout as apiLogout,
  register as apiRegister,
  updateNewsletter,
  getNewsletter,
  subscribeNewsletter,
  updateProfile,
} from "../services/authService";
import type { User } from "../types/User";
import type { AuthContextType } from "../types/context/auth";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string[]> | null>(
    null
  );

  /** Login */
  const login = (access: string, refreshToken: string) => {
    Cookies.set("token", access);
    Cookies.set("refresh", refreshToken);
    fetchUser();
    setLoading(false);
    setError(null);
  };

  /** Register */
  const register = useCallback(
    async (userData: { username: string; email: string; password: string }) => {
      try {
        const response = await apiRegister(userData);

        if (response && response.status === 201) {
          login(response.access, response.refresh);
          fetchUser();
        }

        setError(null);
        return response;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        console.error("Registration failed", err);

        if (err.response?.data) {
          setError(err.response.data);
          setFormErrors(err.response.data);
        } else {
          setError("Registration failed");
        }

        throw err;
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  /** Logout */
  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch (err) {
      console.error("Logout failed", err);
      setError("Logout failed");
    }
    Cookies.remove("refresh");
    Cookies.remove("token");
    setUser(null);
    setLoading(false);
    setError(null);
  }, []);

  /** Refresh token */
  const refreshAccessToken = useCallback(async () => {
    if (!Cookies.get("refresh")) {
      return;
    }
    try {
      const data = await refresh(Cookies.get("refresh") || "");
      const { access, refresh: newRefresh } = data;
      Cookies.set("token", access);
      Cookies.set("refresh", newRefresh);
    } catch (err) {
      console.error("Error refreshing token", err);
      logout();
    }
  }, [logout]);

  /** Fetch current user */
  const fetchUser = useCallback(async () => {
    try {
      const user = await getMe();
      setUser(user);
      setError(null);
    } catch (err) {
      console.error("Error fetching user", err);
      setError("Failed to fetch user");
    } finally {
      setLoading(false);
    }
  }, []);

  /** Newsletter: public subscription */
  const publicSubscribeNewsletter = useCallback(async (email: string) => {
    try {
      const response = await subscribeNewsletter(email);
      return response;
    } catch (err) {
      console.error("Public subscription failed", err);
      throw err;
    }
  }, []);

  /** Newsletter: get current user subscription (auth only) */
  const getMyNewsletter = useCallback(async () => {
    try {
      const response = await getNewsletter();
      return response;
    } catch (err) {
      console.error("Fetching newsletter failed", err);
      throw err;
    }
  }, []);

  /** Newsletter: update current user subscription (auth only) */
  const updateMyNewsletter = useCallback(async (subscribed: boolean) => {
    try {
      const response = await updateNewsletter({ subscribed });
      return response;
    } catch (err) {
      console.error("Updating newsletter failed", err);
      throw err;
    }
  }, []);

  /** Update user profile */
  const profilesUpdate = useCallback(async (updateData: Partial<User>) => {
    try {
      await updateProfile(updateData);
      // Merge updates into local user state
      setUser((prev) => (prev ? { ...prev, ...updateData } : prev));
      setError(null);
    } catch (err) {
      console.error("Error updating profile", err);
      setError("Failed to update profile");
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /** On mount */
  useEffect(() => {
    if (Cookies.get("token")) {
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
      value={{
        user,
        login,
        logout,
        register,
        refreshAccessToken,
        loading,
        error,
        formErrors,
        setLoading,
        setFormErrors,
        setError: (msg: string | null) => setError(msg),
        setUser: (userData: User | null) => setUser(userData),
        publicSubscribeNewsletter,
        getMyNewsletter,
        updateMyNewsletter,
        profilesUpdate,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuthContext = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return ctx;
};
