import { Box, Heading, Text, VStack, Button, Spinner } from "@chakra-ui/react";
import { useBookings } from "../../hooks/useBookings";

export default function BookingList() {
  const { bookings, loading, handleEndBooking } = useBookings();

  if (loading) return <Spinner size="lg" />;

  return (
    <Box p={6}>
      <Heading size="lg" mb={4}>My Bookings</Heading>
      <VStack align="stretch" spacing={3}>
        {bookings.map((b) => (
          <Box key={b.id} p={4} borderWidth="1px" borderRadius="lg">
            <Text><b>Spot:</b> {b.spot_name}</Text>
            <Text><b>Start:</b> {new Date(b.start_time).toLocaleString()}</Text>
            <Text><b>End:</b> {new Date(b.end_time).toLocaleString()}</Text>
            <Button size="sm" mt={2} onClick={() => handleEndBooking(b.id)}>
              End Booking
            </Button>
          </Box>
        ))}
        {bookings.length === 0 && <Text>No active bookings.</Text>}
      </VStack>
    </Box>
  );
}
