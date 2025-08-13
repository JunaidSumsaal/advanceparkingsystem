import React from "react";
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
    title: "Budget Tracking Made Easy",
    text: "Quickly create, manage, and monitor your budgets with real-time insights."
  },
  {
    id: 2,
    title: "Expense Management",
    text: "Easily log, categorize, and review your expenses with detailed breakdowns."
  },
  {
    id: 3,
    title: "Smart Analytics",
    text: "Gain powerful insights into your spending habits with interactive charts and trends."
  },
  {
    id: 4,
    title: "Mobile-First Experience",
    text: "Enjoy a seamless, responsive experience across mobile, tablet, and desktop devices."
  }
];

export default function Features() {
  return (
    <Box p={4}>
      <Stack spacing={4} as={Container} maxW={"3xl"} textAlign={"center"}>
        <Heading fontSize={"3xl"} color={'primary.400'}>Explore What <span className="text-gray-700">SmartSpend Offers</span></Heading>
        <Text color={"gray.600"} fontSize={"xl"}>
        From budget tracking to insightful reports, SmartSpend empowers you with tools to manage your finances effortlessly. Designed for reliability and flexibility, it’s your ultimate financial companion.
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
