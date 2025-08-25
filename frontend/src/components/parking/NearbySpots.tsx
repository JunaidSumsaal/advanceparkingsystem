import { Box, Button, VStack, Heading, Text } from "@chakra-ui/react";
import { useNearbySpots } from "../../hooks/useNearbySpots";

export default function NearbySpots() {
  const { spots, loading, handleBookSpot } = useNearbySpots();

  if (loading) return <Text>Loading nearby spots...</Text>;

  return (
    <Box p={6}>
      <Heading size="lg" mb={4}>Nearby Spots</Heading>
      <VStack spacing={3} align="stretch">
        {spots.map((spot) => (
          <Box key={spot.id} p={4} borderWidth="1px" borderRadius="lg">
            <Text><b>{spot.name}</b></Text>
            <Text>Available: {spot.is_available ? "Yes" : "No"}</Text>
            {spot.is_available && (
              <Button mt={2} onClick={() => handleBookSpot(spot.id)}>
                Book Now
              </Button>
            )}
          </Box>
        ))}
        {spots.length === 0 && <Text>No nearby spots found.</Text>}
      </VStack>
    </Box>
  );
}
