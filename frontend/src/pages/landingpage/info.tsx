import {
  Box,
  Heading,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  Text,
  Container
} from '@chakra-ui/react';
import { ChevronDownIcon } from '@chakra-ui/icons';

export default function Info() {
  return (
    <Box
      textAlign="center"
      py={10}
      px={6}
      gap={4}
      alignItems="center"
      display="flex"
      flexDirection="column"
    >
      <Heading as="h2" size="xl" mt={6} mb={2}>
        Why <Text as='span' color="primary.400">AdvanceParkingSystem</Text> is Right for You
      </Heading>
      <Text color="gray.500">
        Choose AdvanceParkingSystem for unmatched efficiency, a user-friendly interface,
        and powerful parking system. Perfect for individuals and small businesses.
      </Text>
      <Container display="flex" flexDirection="column" alignItems="center">
        <Accordion allowMultiple width="100%" minW="4xl" rounded="lg">
          <AccordionItem>
            <AccordionButton
              display="flex"
              alignItems="center"
              justifyContent="space-between"
              p={4}
            >
              <Text fontSize="md">Effortless Parking, Anytime, Anywhere</Text>
              <ChevronDownIcon fontSize="24px" />
            </AccordionButton>
            <AccordionPanel pb={4}>
              <Text color="gray.600">
                Choose AdvanceParkingSystem for unmatched efficiency, a user-friendly interface, and powerful real-time parking tools. Perfect for drivers, commuters, and facility managers.
              </Text>
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <AccordionButton
              display="flex"
              alignItems="center"
              justifyContent="space-between"
              p={4}
            >
              <Text fontSize="md">Real-Time Parking Insights</Text>
              <ChevronDownIcon fontSize="24px" />
            </AccordionButton>
            <AccordionPanel pb={4}>
              <Text color="gray.600">
                With AdvanceParkingSystem, you can easily monitor parking availability, spot locations, and costs without hassle.
              </Text>
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <AccordionButton
              display="flex"
              alignItems="center"
              justifyContent="space-between"
              p={4}
            >
              <Text fontSize="md">Built for Everyone</Text>
              <ChevronDownIcon fontSize="24px" />
            </AccordionButton>
            <AccordionPanel pb={4}>
              <Text color="gray.600">
                The platform is designed with simplicity and functionality in mind, making it perfect for both individual drivers and large parking operators.
              </Text>
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <AccordionButton
              display="flex"
              alignItems="center"
              justifyContent="space-between"
              p={4}
            >
              <Text fontSize="md">Seamless Across All Devices</Text>
              <ChevronDownIcon fontSize="24px" />
            </AccordionButton>
            <AccordionPanel pb={4}>
              <Text color="gray.600">
                Whether you’re at your desk or on the go, AdvanceParkingSystem adapts to your device and ensures a seamless experience.
              </Text>
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <AccordionButton
              display="flex"
              alignItems="center"
              justifyContent="space-between"
              p={4}
            >
              <Text fontSize="md">Secure, Reliable, and Fast</Text>
              <ChevronDownIcon fontSize="24px" />
            </AccordionButton>
            <AccordionPanel pb={4}>
              <Text color="gray.600">
                From secure authentication to lightning-fast performance, AdvanceParkingSystem gives you everything you need to make parking stress-free.
              </Text>
            </AccordionPanel>
          </AccordionItem>
        </Accordion>
      </Container>
    </Box>
  );
}
