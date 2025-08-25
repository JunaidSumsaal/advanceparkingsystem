/* eslint-disable @typescript-eslint/no-explicit-any */
import { Box, Heading, Spinner, VStack } from "@chakra-ui/react";
import { useParkingService } from "../../hooks/useParkingService";
import ParkingSpotCard from "./ParkingSpotCard";
import { useNearbySpots } from "../../hooks/useNearbySpots";
;

const ParkingSpotPage = () => {
  const { loading, bookParkingSpot } = useParkingService();
  const {spots} = useNearbySpots();

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
