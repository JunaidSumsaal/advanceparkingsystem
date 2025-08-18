import { useAuth } from './useAuth';

export const useIsAuthenticated = () => {
  const { user, loading, error } = useAuth();
  return { isAuthenticated: !!user, loading, error };
};
