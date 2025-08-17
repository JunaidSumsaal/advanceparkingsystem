import type { User } from "../User";

export interface AuthContextType {
  user: User | null;
  users: User[];
  login: (token: string, refresh: string) => void;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  loading: boolean;
  error: string | null;
  currentPage: number;
  setCurrentPage: (page: number) => void;
}
