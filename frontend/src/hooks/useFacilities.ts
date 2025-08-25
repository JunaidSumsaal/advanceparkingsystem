/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback } from "react";
import { archiveFacility, getFacilities, restoreFacility } from "../services/parkingServices";

export const useFacilities = () => {
  const [facilities, setFacilities] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchFacilities = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getFacilities();
      setFacilities(data.results || []);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleArchive = async (id: number) => {
    await archiveFacility(id);
    fetchFacilities();
  };

  const handleRestore = async (id: number) => {
    await restoreFacility(id);
    fetchFacilities();
  };

  useEffect(() => {
    fetchFacilities();
  }, [fetchFacilities]);

  return { facilities, loading, handleArchive, handleRestore };
};
