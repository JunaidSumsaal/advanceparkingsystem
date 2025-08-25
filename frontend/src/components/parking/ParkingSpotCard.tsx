/* eslint-disable @typescript-eslint/no-explicit-any */
import { Box, Text, Button, VStack } from "@chakra-ui/react";

const ParkingSpotCard = ({ spot, onBook }: { spot: any, onBook: any }) => {
  return (
    <Box borderWidth="1px" borderRadius="md" p={4} mb={4} bg={spot.is_available ? "green.100" : "red.100"}>
      <VStack align="start">
        <Text fontSize="lg" fontWeight="bold">{spot.name}</Text>
        <Text fontSize="sm">Price: {spot.price_per_hour} / hr</Text>
        <Text fontSize="sm">{spot.is_available ? "Available" : "Not Available"}</Text>
        {spot.is_available && (
          <Button colorScheme="blue" onClick={() => onBook(spot.id)}>Book Spot</Button>
        )}
      </VStack>
    </Box>
  );
};

export default ParkingSpotCard;
