/* eslint-disable @typescript-eslint/no-explicit-any */
export interface User {
  email: string;
  gender?: string;
  location?: string;
  phone?: string;
  verified?: string;
  primaryEmail?: string;
  role?: string;
  username: string;
}


export interface Loading {
  loading: any | string | null;
}

export interface Error {
  message: string;
}