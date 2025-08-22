import { useUsersContext } from '../context/UsersContext';
import { useAuth } from './useAuth';

export const useAdminUsers = () => {
  const { user } = useAuth();
  const { users, currentPage, setCurrentPage, loading, error, totalPages, roleFilter, setRoleFilter, refreshUsers } = useUsersContext();

  const isAdmin = user?.role === 'admin';
  return {
    isAdmin,
    users,
    loading,
    error,
    currentPage,
    totalPages,
    roleFilter,
    setCurrentPage,
    setRoleFilter,
    refreshUsers
  };
};
