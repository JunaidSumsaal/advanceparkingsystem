export interface User {
  id: string;
  username: string;
  email: string;
  password?: string;
  isAdmin?: boolean;
  role: string;
}


export interface Credentials {
  username: string;
  email?: string;
  password: string;
}