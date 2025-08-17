import { useContext } from 'react';
import { AuthContext } from '../context/Auth';
import type { AuthContextType } from '../types/context/auth';

export const useAuth = (): AuthContextType => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
};
