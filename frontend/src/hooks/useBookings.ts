/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback } from "react";
import { getBookings, bookSpot, endBooking } from "../services/parkingServices";

export const useBookings = () => {
  const [bookings, setBookings] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchBookings = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getBookings();
      setBookings(data.results || []);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleBookSpot = async (spot: number, start: string, end: string) => {
    const data = await bookSpot({ spot, start_time: start, end_time: end });
    fetchBookings();
    return data;
  };

  const handleEndBooking = async (id: number) => {
    await endBooking(id);
    fetchBookings();
  };

  useEffect(() => {
    fetchBookings();
  }, [fetchBookings]);

  return { bookings, loading, handleBookSpot, handleEndBooking };
};
