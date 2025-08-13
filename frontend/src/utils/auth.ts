import { getMe } from '@services/authService';

export const isAuthenticated = async (): Promise<boolean> => {
  try {
  
    const token = localStorage.getItem('token');
    if (!token) {
      return false;
    }
    const user = await getMe(); 
    return !!user;
  } catch (err) {
    console.error("Error during authentication check:", err);
    return false;
  }
};
