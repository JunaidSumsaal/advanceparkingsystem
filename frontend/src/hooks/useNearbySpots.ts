/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback } from "react";
import { getNearbySpots, bookSpot } from "../services/parkingServices";

export const useNearbySpots = () => {
  const [spots, setSpots] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchSpots = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getNearbySpots();
      setSpots(data.results || []);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleBook = async (spotId: number) => {
    const now = new Date();
    const start_time = now.toISOString();
    const end_time = new Date(now.getTime() + 60 * 60 * 1000).toISOString(); // +1hr
    await bookSpot({ spot: spotId, start_time, end_time });
    fetchSpots();
  };

  useEffect(() => {
    fetchSpots();
  }, [fetchSpots]);

  return { spots, loading, handleBook };
};
