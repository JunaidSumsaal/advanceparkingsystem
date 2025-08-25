import { Box, Heading, VStack, Text, Button } from "@chakra-ui/react";
import { usePricing } from "../../hooks/usePricing";

export default function PricingPanel() {
  const { logs, loading, handleUpdatePricing } = usePricing();

  if (loading) return <Text>Loading pricing logs...</Text>;

  return (
    <Box>
      <Heading size="md" mb={4}>Dynamic Pricing</Heading>
      <Button colorScheme="blue" size="sm" mb={4} onClick={handleUpdatePricing}>
        Update Pricing
      </Button>
      <VStack align="stretch" spacing={4}>
        {logs.map((log, idx) => (
          <Box key={idx} borderWidth="1px" borderRadius="md" p={4}>
            <Text><strong>Spot:</strong> {log.spot}</Text>
            <Text><strong>Old Price:</strong> {log.old_price}</Text>
            <Text><strong>New Price:</strong> {log.new_price}</Text>
            <Text><strong>Updated:</strong> {new Date(log.timestamp).toLocaleString()}</Text>
          </Box>
        ))}
        {logs.length === 0 && <Text>No pricing logs available.</Text>}
      </VStack>
    </Box>
  );
}
