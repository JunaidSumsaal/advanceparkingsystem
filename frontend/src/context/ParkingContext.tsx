import React, { createContext, useContext, useState, useCallback } from "react";
import {
  getBookings,
  getBooking,
  bookSpot,
  endBooking,
  getFacilities,
  getFacility,
  getNearbySpots,
  navigateToSpot,
  createSpotReview,
} from "../services/parkingApi";
import type { ParkingContextType, Booking, Facility, Spot } from "../types/context/parking";

const ParkingContext = createContext<ParkingContextType | undefined>(undefined);

export const ParkingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [nearbySpots, setNearbySpots] = useState<Spot[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBookings = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getBookings();
      setBookings(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch bookings");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchBooking = useCallback(async (id: number) => {
    try {
      setLoading(true);
      const res = await getBooking(id);
      setError(null);
      return res;
    } catch (err) {
      console.error(err);
      setError("Failed to fetch booking");
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const makeBooking = useCallback(async (data: { spot: number; start_time: string; end_time: string }) => {
    try {
      const res = await bookSpot(data);
      await fetchBookings();
      return res;
    } catch (err) {
      console.error(err);
      throw err;
    }
  }, [fetchBookings]);

  const endExistingBooking = useCallback(async (id: number) => {
    try {
      const res = await endBooking(id);
      await fetchBookings();
      return res;
    } catch (err) {
      console.error(err);
      throw err;
    }
  }, [fetchBookings]);

  const fetchFacilities = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getFacilities();
      setFacilities(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch facilities");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchFacility = useCallback(async (id: number) => {
    try {
      setLoading(true);
      const res = await getFacility(id);
      setError(null);
      return res;
    } catch (err) {
      console.error(err);
      setError("Failed to fetch facility");
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchNearbySpots = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getNearbySpots();
      setNearbySpots(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch nearby spots");
    } finally {
      setLoading(false);
    }
  }, []);

  const navigateTo = useCallback(async (spotId: number) => {
    try {
      const res = await navigateToSpot(spotId);
      return res;
    } catch (err) {
      console.error(err);
      throw err;
    }
  }, []);

  const createReview = useCallback(async (data: { spot: number; rating: number; comment?: string }) => {
    try {
      const res = await createSpotReview(data);
      return res;
    } catch (err) {
      console.error(err);
      throw err;
    }
  }, []);

  return (
    <ParkingContext.Provider
      value={{
        bookings,
        facilities,
        nearbySpots,
        fetchBookings,
        fetchBooking,
        makeBooking,
        endBooking: endExistingBooking,
        fetchFacilities,
        fetchFacility,
        fetchNearbySpots,
        navigateToSpot: navigateTo,
        createSpotReview: createReview,
        setError,
        setLoading,
        loading,
        error,
      }}
    >
      {children}
    </ParkingContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useParkingContext = () => {
  const ctx = useContext(ParkingContext);
  if (!ctx) throw new Error("useParkingContext must be used within ParkingProvider");
  return ctx;
};
