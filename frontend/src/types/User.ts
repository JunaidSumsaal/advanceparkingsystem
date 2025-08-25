export interface User {
  id: number | string | null;
  username?: string | null;
  email?: string;
  password?: string | null;
  password_confirm?: string | null;
  first_name?: string;
  last_name?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  is_active?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
  role: string | null;
  default_radius_km?: string
}

export type Role = "driver" | "provider" | "attendant" | "admin" | null;


export interface Credentials {
  username: string;
  email?: string;
  password: string;
}