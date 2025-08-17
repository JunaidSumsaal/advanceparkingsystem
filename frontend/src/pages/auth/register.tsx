/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from "react";
import {
  Flex,
  Box,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  HStack,
  InputRightElement,
  Stack,
  Button,
  Heading,
  Text,
  useColorModeValue,
  useToast,
  Image,
  Link as ChakraLink,
} from "@chakra-ui/react";
import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons";
import { Link, useNavigate } from "react-router-dom";
import Logo from "../../assets/header_logo.png";
import { register as registerService } from "../../services/authService";
import { useAuth } from "../../hooks/useAuth";

export default function Register() {
  const [showPassword, setShowPassword] = useState(false);
  const [userData, setUserData] = useState({
    username: "",
    email: "",
    password: "",
    password_confirm: "",
  });
  const [loading, setLoading] = useState(false);
  const { login: authLogin } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserData({ ...userData, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (userData.password !== userData.password_confirm) {
      toast({
        title: "Passwords do not match",
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "top",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await registerService({
        username: userData.username,
        email: userData.email,
        password: userData.password,
      });

      if (response.access && response.refresh) {
        authLogin(response.access, response.refresh);
        toast({
          title: "Registration successful!",
          description: "Welcome to APS!",
          status: "success",
          duration: 3000,
          isClosable: true,
          position: "top",
        });
        navigate("/dashboard");
      } else {
        toast({
          title: "Registration failed",
          description: response.message || "Something went wrong.",
          status: "error",
          duration: 3000,
          isClosable: true,
          position: "top",
        });
      }
    } catch (error: any) {
      toast({
        title: "Registration failed",
        description: error.response?.data?.message || "Something went wrong.",
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "top",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex
      minH={"100vh"}
      align={"center"}
      justify={"center"}
      bg={useColorModeValue("gray.50", "gray.800")}
    >
      <Stack spacing={8} mx={"auto"} maxW={"lg"} py={12} px={6}>
        <Stack align={"center"}>
          <Box as={Link} to="/">
            <Image src={Logo} alt="APS" h="60px" />
          </Box>
          <Heading fontSize={"4xl"} textAlign={"center"}>
            Sign up
          </Heading>
          <Text fontSize={"lg"} color={"gray.600"}>
            to enjoy all of our cool features ✌️
          </Text>
        </Stack>
        <Box
          rounded={"lg"}
          bg={useColorModeValue("white", "gray.700")}
          boxShadow={"lg"}
          p={8}
        >
          <form onSubmit={handleSubmit}>
            <Stack spacing={4}>
              <HStack>
                <Box>
                  <FormControl id="username" isRequired>
                    <FormLabel>Username</FormLabel>
                    <Input
                      type="text"
                      focusBorderColor="primary.400"
                      onChange={handleChange}
                      value={userData.username}
                    />
                  </FormControl>
                </Box>
              </HStack>

              <FormControl id="email" isRequired>
                <FormLabel>Email address</FormLabel>
                <Input
                  type="email"
                  onChange={handleChange}
                  value={userData.email}
                  focusBorderColor="primary.400"
                />
              </FormControl>

              <FormControl id="password" isRequired>
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword ? "text" : "password"}
                    focusBorderColor="primary.400"
                    onChange={handleChange}
                    value={userData.password}
                  />
                  <InputRightElement h={"full"}>
                    <Button
                      variant={"ghost"}
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <ViewIcon /> : <ViewOffIcon />}
                    </Button>
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              <FormControl id="password_confirm" isRequired>
                <FormLabel>Confirm Password</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword ? "text" : "password"}
                    focusBorderColor="primary.400"
                    onChange={handleChange}
                    value={userData.password_confirm}
                  />
                  <InputRightElement h={"full"}>
                    <Button
                      variant={"ghost"}
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <ViewIcon /> : <ViewOffIcon />}
                    </Button>
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              <Stack spacing={10} pt={2}>
                <Button
                  type="submit"
                  size="lg"
                  bg={"primary.400"}
                  color={"white"}
                  _hover={{ bg: "primary.500" }}
                  isLoading={loading}
                  loadingText="Submitting"
                >
                  Register
                </Button>
              </Stack>
            </Stack>
          </form>

          <Stack pt={6}>
            <Text align={"center"}>
              Already a user?{" "}
              <ChakraLink
                as={Link}
                to="/login"
                color="primary.400"
                _hover={{ color: "primary.500" }}
              >
                Login
              </ChakraLink>
            </Text>
          </Stack>
        </Box>
      </Stack>
    </Flex>
  );
}
