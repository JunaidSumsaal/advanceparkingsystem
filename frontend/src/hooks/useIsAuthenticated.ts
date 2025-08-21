import { useAuthContext } from '../context/AuthContext';

export const useIsAuthenticated = () => {
  const { user, loading, error } = useAuthContext();

  const isAuthenticated = !loading && !!user;

  return { isAuthenticated, user, loading, error };
};
