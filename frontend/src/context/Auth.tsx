import { createContext } from "react";
import type { AuthContextType } from "../types/context/auth";

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);
