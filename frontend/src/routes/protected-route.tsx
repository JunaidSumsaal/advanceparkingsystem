import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import LoaderDash from '../components/loader/loaders-dashboard';
import { useToast } from '@chakra-ui/react';
import { isAuthenticated } from '../utils/auth';

export const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    const checkAuthentication = async () => {
      try {
        setLoading(true);
        const authStatus = await isAuthenticated();
        setAuthenticated(authStatus);
      } catch (err) {
        toast({
          title: 'Error',
          description: 'An error occurred while checking for authentication.',
          status: 'error',
          duration: 9000,
          isClosable: true,
          position: 'top'
        });
        setAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuthentication();
  }, [toast]);

  if (loading) {
    return <LoaderDash />;
  } else if (authenticated) {
    return children;
  } else {
    return <Navigate to='/login' replace />;
  }
};
