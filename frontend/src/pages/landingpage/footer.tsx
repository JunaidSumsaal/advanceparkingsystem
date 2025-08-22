import { useState } from "react";
import {
  Box,
  chakra,
  Container,
  SimpleGrid,
  Stack,
  Text,
  VisuallyHidden,
  Input,
  IconButton,
  useColorModeValue,
  Image,
  useToast,
} from "@chakra-ui/react";
import type { ReactNode } from "react";
import { FaInstagram, FaTwitter, FaYoutube } from "react-icons/fa";
import { BiMailSend } from "react-icons/bi";
import Logo from "../../assets/header_logo.png";
import { useAuth } from "../../hooks/useAuth";

const SocialButton = ({
  children,
  label,
  href,
}: {
  children: ReactNode;
  label: string;
  href: string;
}) => {
  return (
    <chakra.button
      bg={useColorModeValue("blackAlpha.100", "whiteAlpha.100")}
      rounded={"full"}
      w={8}
      h={8}
      cursor={"pointer"}
      as={"a"}
      href={href}
      display={"inline-flex"}
      alignItems={"center"}
      justifyContent={"center"}
      transition={"background 0.3s ease"}
      _hover={{
        bg: useColorModeValue("blackAlpha.200", "whiteAlpha.200"),
      }}
    >
      <VisuallyHidden>{label}</VisuallyHidden>
      {children}
    </chakra.button>
  );
};

const ListHeader = ({ children }: { children: ReactNode }) => {
  return (
    <Text fontWeight={"500"} fontSize={"lg"} mb={2}>
      {children}
    </Text>
  );
};

export default function Footer() {
  const today = new Date();
  const currentYear = today.getFullYear().toString();
  const { publicSubscribeNewsletter, loading: loader } = useAuth();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(loader);
  const toast = useToast();

  const handleSubscribe = async () => {
    if (!email) {
      toast({
        title: "Please enter an email",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      setLoading(true);
      await publicSubscribeNewsletter(email);
      setEmail("");
      toast({
        title: "Subscribed successfully",
        description: "You are now subscribed to our newsletter.",
        status: "success",
        duration: 4000,
        isClosable: true,
        position: "top",
      });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      toast({
        title: "Subscription failed",
        description: err?.response?.data?.email || "Please try again later.",
        status: "error",
        duration: 4000,
        isClosable: true,
        position: "top",
      });
    } finally {
      setLoading(false);
    }
  };
  return (
    <Box color={useColorModeValue("gray.700", "gray.200")}>
      <Container as={Stack} maxW={"6xl"} py={10}>
        <SimpleGrid
          templateColumns={{ sm: "1fr 1fr", md: "2fr 1fr 1fr 2fr" }}
          spacing={8}
        >
          <Stack spacing={6}>
            <Box>
              <Text
                as="h2"
                fontSize="2xl"
                fontFamily="monospace"
                fontWeight="bold"
                className="flex gap-2"
                color={"primary.400"}
              >
                <Image src={Logo} alt="APS" h="30px" />
                APS
              </Text>
            </Box>
            <Text fontSize={"sm"}>
              © {currentYear} AdvanceParkingSystem. All rights reserved
            </Text>
            <Stack direction={"row"} spacing={6}>
              <SocialButton label={"Twitter"} href={"#"}>
                <FaTwitter />
              </SocialButton>
              <SocialButton label={"YouTube"} href={"#"}>
                <FaYoutube />
              </SocialButton>
              <SocialButton label={"Instagram"} href={"#"}>
                <FaInstagram />
              </SocialButton>
            </Stack>
          </Stack>
          <Stack align={"flex-start"}>
            <ListHeader>Company</ListHeader>
            <Box as="a" href={"#"}>
              About us
            </Box>
            <Box as="a" href={"#"}>
              Blog
            </Box>
            <Box as="a" href={"#"}>
              Contact us
            </Box>
            <Box as="a" href={"#"}>
              Pricing
            </Box>
            <Box as="a" href={"#"}>
              Testimonials
            </Box>
          </Stack>
          <Stack align={"flex-start"}>
            <ListHeader>Support</ListHeader>
            <Box as="a" href={"#"}>
              Help Center
            </Box>
            <Box as="a" href={"#"}>
              Terms of Service
            </Box>
            <Box as="a" href={"#"}>
              Legal
            </Box>
            <Box as="a" href={"#"}>
              Privacy Policy
            </Box>
            <Box as="a" href={"#"}>
              Status
            </Box>
          </Stack>
          <Stack align={"flex-start"}>
            <ListHeader>Stay up to date</ListHeader>
            <Stack direction={"row"}>
              <Input
                type="email"
                placeholder={"Your email address"}
                aria-label="Subscribe to newsletter"
                bg={useColorModeValue("blackAlpha.100", "whiteAlpha.100")}
                border={0}
                focusBorderColor="primary.400"
                _focus={{
                  bg: "whiteAlpha.300",
                }}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <IconButton
                bg={useColorModeValue("primary.400", "primary.800")}
                color={useColorModeValue("white", "gray.800")}
                _hover={{
                  bg: "primary.600",
                }}
                aria-label="Subscribe"
                icon={<BiMailSend />}
                onClick={handleSubscribe}
                isLoading={loading}
              />
            </Stack>
          </Stack>
        </SimpleGrid>
      </Container>
    </Box>
  );
}
