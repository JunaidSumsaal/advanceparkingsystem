import { useAuthContext } from '../context/AuthContext';

export const useAuth = () => {
  const { user, login, logout, refreshAccessToken, loading, error, register, formErrors, setLoading, setError, setFormErrors, setUser, publicSubscribeNewsletter, getMyNewsletter, updateMyNewsletter, profilesUpdate } = useAuthContext();
  return { user, login, logout, refreshAccessToken, loading, error, register, formErrors, setLoading, setError, setFormErrors, setUser, publicSubscribeNewsletter, getMyNewsletter, updateMyNewsletter, profilesUpdate  };
};
