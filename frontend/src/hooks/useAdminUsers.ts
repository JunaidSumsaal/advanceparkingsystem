import { useUsersContext } from '../context/UsersContext';
import { useAuth } from './useAuth';

export const useAdminUsers = () => {
  const { user } = useAuth();
  const { users, currentPage, setCurrentPage, fetchUsers, loading, error } = useUsersContext();

  const isAdmin = user?.role === 'admin';
  return {
    isAdmin,
    users: isAdmin ? users : [],
    currentPage,
    setCurrentPage,
    fetchUsers,
    loading,
    error,
  };
};
