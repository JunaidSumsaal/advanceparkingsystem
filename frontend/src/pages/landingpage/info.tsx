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
        Why <span className="text-primary-400">SmartSpend</span> is Right for You
      </Heading>
      <Text color="gray.500">
        Choose SmartSpend for unmatched efficiency, a user-friendly interface,
        and powerful budgeting tools. Perfect for individuals and teams
        managing diverse financial goals.
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
              <Text fontSize="md">Effortless Expense Tracking</Text>
              <ChevronDownIcon fontSize="24px" />
            </AccordionButton>
            <AccordionPanel pb={4}>
              <Text color="gray.600">
                With SmartSpend, you can easily monitor spending, budgets, and savings without hassle.
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
              <Text fontSize="md">User-Centric Design</Text>
              <ChevronDownIcon fontSize="24px" />
            </AccordionButton>
            <AccordionPanel pb={4}>
              <Text color="gray.600">
                The platform is designed with simplicity and functionality in mind,
                making it perfect for both individuals and finance teams.
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
              <Text fontSize="md">Flexibility Across Devices</Text>
              <ChevronDownIcon fontSize="24px" />
            </AccordionButton>
            <AccordionPanel pb={4}>
              <Text color="gray.600">
                Whether you’re at your desk or on the go, SmartSpend adapts to
                your device and ensures a seamless experience.
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
              <Text fontSize="md">Real-Time Financial Updates</Text>
              <ChevronDownIcon fontSize="24px" />
            </AccordionButton>
            <AccordionPanel pb={4}>
              <Text color="gray.600">
                Add expenses, adjust budgets, and track savings with real-time synchronization across your account.
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
              <Text fontSize="md">Built for Modern Financial Needs</Text>
              <ChevronDownIcon fontSize="24px" />
            </AccordionButton>
            <AccordionPanel pb={4}>
              <Text color="gray.600">
                From secure authentication to lightning-fast performance,
                SmartSpend gives you everything you need to master your finances easily.
              </Text>
            </AccordionPanel>
          </AccordionItem>
        </Accordion>
      </Container>
    </Box>
  );
}
