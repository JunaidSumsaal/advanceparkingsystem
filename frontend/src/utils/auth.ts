import { getMe } from '../services/authService';
import Cookie from 'js-cookie';

export const isAuthenticated = async (): Promise<boolean> => {
  try {
  
    const token = Cookie.get('token');
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
