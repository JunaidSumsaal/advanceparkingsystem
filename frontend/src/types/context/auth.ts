/* eslint-disable @typescript-eslint/no-explicit-any */
import type { User } from "../User";

export interface AuthContextType {
  user: User | null;
  users?: User[];
  login: (token: string, refresh: string) => void;
  logout: () => void;
  register: (
    userData: { username: string; email: string; password: string }
  ) => Promise<any>;
  refreshAccessToken?: () => Promise<void>;
  loading: boolean;
  error: string | null;
  formErrors: Record<string, string[]> | null;
  setLoading?: (loading: boolean) => void;
  setError?: (error: string | null) => void;
  setFormErrors?: (errors: Record<string, string[]> | null) => void;
  setUser?: (user: User | null) => void;
  setUsers?: (users: User[]) => void;
  fetchUser?: () => Promise<void>;
  isAuthenticated?: boolean;
  totalUsers?: number;
  totalPages?: number;
  currentPage?: number;
  setCurrentPage?: (page: number) => void;
}
