/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from "react";
import { getNearbySpots, bookSpot, getSpotAvailabilityLogs } from "../services/parkingServices";

export const useParkingService = () => {
  const [spots, setSpots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch available parking spots
  const fetchAvailableSpots = async (latitude: string, longitude: string) => {
    setLoading(true);
    try {
      const response = await getNearbySpots({ lat: latitude, lng: longitude });
      setSpots(response);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  // Book parking spot
  const bookParkingSpot = async (spotId: number, startTime: string, endTime: string) => {
    try {
      await bookSpot({ spot: spotId, start_time: startTime, end_time: endTime })
      .then((params: any) => {
      fetchAvailableSpots(params.latitude, params.longitude);
      })
    } catch (err: any) {
      setError(err);
    }
  };

  // Fetch spot availability logs
  const fetchAvailabilityLogs = async (spotId: number) => {
    try {
      const logs = await getSpotAvailabilityLogs({ spot: spotId });
      return logs;
    } catch (err: any) {
      setError(err);
    }
  };

  return {
    spots,
    loading,
    error,
    fetchAvailableSpots,
    bookParkingSpot,
    fetchAvailabilityLogs,
  };
};
