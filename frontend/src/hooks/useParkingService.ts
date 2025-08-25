/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from "react";
import { createBooking, getSpotAvailabilityLogs } from "../services/parkingServices";
import { useNearbySpots } from "./useNearbySpots";

export const useParkingService = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { fetchSpots } = useNearbySpots()

  // Book parking spot
  const bookParkingSpot = async (spotId: number, startTime: string, endTime: string) => {
    setLoading(true);
    try {
      await createBooking({ spot: spotId, start_time: startTime, end_time: endTime })
      .then(() => {
      fetchSpots();
      })
      setLoading(false);
    } catch (err: any) {
      setError(err);
      setLoading(false);
    }
  };

  // Fetch spot availability logs
  const fetchAvailabilityLogs = async (spotId: number) => {
    setLoading(true);
    try {
      const logs = await getSpotAvailabilityLogs({ spot: spotId });
      setLoading(false);
      return logs;
    } catch (err: any) {
      setError(err);
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    bookParkingSpot,
    fetchAvailabilityLogs,
  };
};
