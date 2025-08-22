import {
  Box,
  Container,
  Heading,
  SimpleGrid,
  Icon,
  Text,
  Stack,
  HStack,
  VStack
} from "@chakra-ui/react";
import { CheckIcon } from "@chakra-ui/icons";

// Replace test data with your own
const features = [
  {
    id: 1,
    title: "Real-Time Spot Availability",
    text: "Quickly find, view, and monitor available parking spots with live updates powered by sensors and geotags."
  },
  {
    id: 2,
    title: "Smart Navigation & Alerts",
    text: "Get guided directions to nearby parking and receive instant notifications when a spot opens up around you."
  },
  {
    id: 3,
    title: "Dynamic Pricing Engine",
    text: "Benefit from fair, transparent pricing that adapts in real-time based on demand and availability."
  },
  {
    id: 4,
    title: "Insights & Reports",
    text: "Access parking history, cost summaries, and usage patterns to better plan your trips and manage expenses."
  }
];

export default function Features() {
  return (
    <Box p={4}>
      <Stack spacing={4} as={Container} maxW={"3xl"} textAlign={"center"}>
        <Heading fontSize={"3xl"} color={'primary.400'}>Explore What <span className="text-gray-700">AdvanceParkingSystem Offers</span></Heading>
        <Text color={"gray.600"} fontSize={"xl"}>
            From real-time spot tracking to smart pricing and instant alerts, AdvanceParkingSystem empowers you with the tools to make parking effortless. Designed for reliability and flexibility, it’s your ultimate parking companion.
        </Text>
      </Stack>

      <Container maxW={"6xl"} mt={10}>
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={10}>
          {features.map((feature) => (
            <HStack key={feature.id} align={"top"}>
              <Box color={"primary.400"} px={2}>
                <Icon as={CheckIcon} />
              </Box>
              <VStack align={"start"}>
                <Text fontWeight={600} color={'gray.700'}>{feature.title}</Text>
                <Text color={"gray.600"}>{feature.text}</Text>
              </VStack>
            </HStack>
          ))}
        </SimpleGrid>
      </Container>
    </Box>
  );
}
