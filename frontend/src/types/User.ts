export interface User {
  id: string;
  username: string;
  email: string;
  password?: string;
  role: string;
  default_radius_km: string
}


export interface Credentials {
  username: string;
  email?: string;
  password: string;
}