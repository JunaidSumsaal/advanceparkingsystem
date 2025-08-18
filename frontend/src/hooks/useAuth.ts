import { useAuthContext } from '../context/AuthContext';

export const useAuth = () => {
  const { user, login, logout, refreshAccessToken, loading, error } = useAuthContext();
  return { user, login, logout, refreshAccessToken, loading, error };
};
