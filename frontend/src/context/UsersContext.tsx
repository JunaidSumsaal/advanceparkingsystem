import React, { createContext, useContext, useEffect, useState } from "react";
import { getUsers } from "../services/authService";
import { useAuth } from "../hooks/useAuth";

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

interface UserContextType {
  users: User[];
  loading: boolean;
  error: string | null;
  currentPage: number;
  totalPages: number;
  roleFilter: string | null;
  setCurrentPage: (page: number) => void;
  setRoleFilter: (role: string | null) => void;
  refreshUsers: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [roleFilter, setRoleFilter] = useState<string | null>(null);

  const loadUsers = async () => {
    if (!user || user.role !== "admin") {
      return;
    }
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page: currentPage };
      if (roleFilter) {
        params.role = roleFilter;
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const res = await getUsers((params as any));
      setUsers(res.results || res.data || []); // adapt to API shape
      setTotalPages(res.total_pages || res.totalPages || 1);
      setError(null);
    } catch (err) {
      setError(`Failed to load users: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, roleFilter]);

  return (
    <UserContext.Provider
      value={{
        users,
        loading,
        error,
        currentPage,
        totalPages,
        roleFilter,
        setCurrentPage,
        setRoleFilter,
        refreshUsers: loadUsers,
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useUsersContext = () => {
  const ctx = useContext(UserContext);
  if (!ctx) {
    throw new Error("useUsersContext must be used inside UserProvider");
  }
  return ctx;
};
