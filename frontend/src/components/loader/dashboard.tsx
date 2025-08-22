import {
  Container,
  useColorModeValue,
  Heading,
  Spinner,
} from "@chakra-ui/react";


export default function Dash() {
  return (
    <>
      <Container
        minH="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
        flexDirection="column"
      >
        <Spinner size="xl" color="primary.400" />
        <Heading
          size="md"
          mt={4}
          fontWeight="500"
          color={useColorModeValue("gray.600", "gray.400")}
        >
          Please wait we&apos;re getting everything ready for you...
        </Heading>
      </Container>
    </>
  );
}
