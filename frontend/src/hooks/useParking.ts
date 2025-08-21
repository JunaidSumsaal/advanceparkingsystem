import { useParkingContext } from '../context/ParkingContext';

export const useParking = () => {
  const {
    bookings,
    facilities,
    nearbySpots,
    fetchBookings,
    fetchBooking,
    makeBooking,
    endBooking,
    fetchFacilities,
    fetchFacility,
    fetchNearbySpots,
    navigateToSpot,
    createSpotReview,
    loading,
    error,
    setError,
    setLoading,
  } = useParkingContext();

  return {
    bookings,
    facilities,
    nearbySpots,
    fetchBookings,
    fetchBooking,
    makeBooking,
    endBooking,
    fetchFacilities,
    fetchFacility,
    fetchNearbySpots,
    navigateToSpot,
    createSpotReview,
    loading,
    error,
    setError,
    setLoading,
  };
};
