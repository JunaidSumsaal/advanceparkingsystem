import React from 'react';
import { Navigate } from 'react-router-dom';
import LoaderDash from '../components/loader/loaders-dashboard';
import { useToast } from '@chakra-ui/react';
import { useIsAuthenticated } from '../hooks/useIsAuthenticated';

export const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, loading, error } = useIsAuthenticated();
  const toast = useToast();

  React.useEffect(() => {
    if (error) {
      toast({
        title: 'Error',
        description: 'An error occurred while checking for authentication.',
        status: 'error',
        duration: 5000,
        isClosable: true,
        position: 'top',
      });
    }
  }, [error, toast]);

  if (loading) {
    return <LoaderDash />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
