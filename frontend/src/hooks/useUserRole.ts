// src/hooks/useUserRole.ts
import { useEffect, useState } from "react";
import { useAuth } from "./useAuth";
import type { Role } from "../types/User";


export const useUserRole = () => {
  const { user } = useAuth();
  const [role, setRole] = useState<Role>("driver");
  const [loading, setLoading] = useState(true);
  const roles = user ? user.role : null

  useEffect(() => {
    const fetchRole = async () => {
      try {
        setRole(roles as Role);
      } catch (err) {
        console.log(err);
        setRole("driver");
      } finally {
        setLoading(false);
      }
    };
    fetchRole();
  }, [roles]);

  return { role, loading };
};
