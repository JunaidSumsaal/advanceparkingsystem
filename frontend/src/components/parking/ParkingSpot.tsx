/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect } from "react";
import { Box, Heading, Spinner, VStack } from "@chakra-ui/react";
import { useParkingService } from "../../hooks/useParkingService";
import ParkingSpotCard from "./ParkingSpotCard";
;

const ParkingSpotPage = ({ latitude, longitude }: {latitude: string, longitude: string }) => {
  const { spots, loading, fetchAvailableSpots, bookParkingSpot } = useParkingService();

  useEffect(() => {
    fetchAvailableSpots(latitude, longitude);
  }, [latitude, longitude, fetchAvailableSpots]);

  const handleBooking = (spotId: number) => {
    const startTime = new Date().toISOString();
    const endTime = new Date(new Date().getTime() + 60 * 60 * 1000).toISOString();
    bookParkingSpot(spotId, startTime, endTime);
  };

  return (
    <Box p={6}>
      <Heading mb={4}>Available Parking Spots</Heading>
      {loading ? (
        <Spinner />
      ) : (
        <VStack spacing={4}>
          {spots.map((spot: any) => (
            <ParkingSpotCard key={spot.id} spot={spot} onBook={handleBooking(spot.id)} />
          ))}
        </VStack>
      )}
    </Box>
  );
};

export default ParkingSpotPage;
