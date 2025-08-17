import { useAuth } from './useAuth';

export const useAdminUsers = () => {
  const { user, users, currentPage, setCurrentPage, loading, error } = useAuth();

  const isAdmin = user?.role === 'admin';

  return {
    isAdmin,
    users: isAdmin ? users : [],
    currentPage,
    setCurrentPage,
    loading,
    error,
  };
};
