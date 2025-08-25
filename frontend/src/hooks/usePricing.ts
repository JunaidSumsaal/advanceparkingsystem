/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback } from "react";
import { getSpotPriceLogs, updateDynamicPricing } from "../services/parkingServices";

export const usePricing = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getSpotPriceLogs();
      setLogs(data.results || []);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleUpdatePricing = async () => {
    await updateDynamicPricing();
    fetchLogs();
  };

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  return { logs, loading, handleUpdatePricing };
};
