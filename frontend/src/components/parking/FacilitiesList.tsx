import { Box, Heading, Text, VStack, Badge } from "@chakra-ui/react";
import { useFacilities } from "../../hooks/useFacilities";

export default function FacilitiesList() {
  const { facilities, loading } = useFacilities();

  if (loading) return <Text>Loading facilities...</Text>;

  return (
    <Box p={6}>
      <Heading size="lg" mb={4}>Facilities</Heading>
      <VStack spacing={3} align="stretch">
        {facilities.map((f) => (
          <Box key={f.id} p={4} borderWidth="1px" borderRadius="lg">
            <Heading size="sm">{f.name}</Heading>
            <Text>{f.address}</Text>
            <Badge colorScheme={f.is_active ? "green" : "red"}>
              {f.is_active ? "Active" : "Inactive"}
            </Badge>
          </Box>
        ))}
        {facilities.length === 0 && <Text>No facilities available.</Text>}
      </VStack>
    </Box>
  );
}
