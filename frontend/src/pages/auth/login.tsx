/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from "react";
import {
  Flex,
  Box,
  FormControl,
  FormLabel,
  Input,
  Checkbox,
  Stack,
  Button,
  Heading,
  Text,
  useColorModeValue,
  InputGroup,
  InputRightElement,
  useToast,
  Image,
  Link as ChakraLink,
} from '@chakra-ui/react';
import { Link, useNavigate } from 'react-router-dom';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import Cookies from 'js-cookie';
import Logo from '../../assets/header_logo.png';
import { login as loginService } from '../../services/authService';
import { useAuth } from '../../context/AuthContext';

export default function Login() {
  const [showPassword, setShowPassword] = useState(false);
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const { login: authLogin } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({
      ...credentials,
      [e.target.id]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await loginService(credentials);
  
      if (response.accessToken && response.refreshToken) {
        Cookies.set('refreshToken', response.refreshToken, { expires: 7 });
        authLogin(response.accessToken);
  
        toast({
          title: 'We are Glad to see You ✌️',
          description: 'Welcome back!',
          status: 'success',
          duration: 3000,
          isClosable: true,
          position: 'top'
        });
        navigate('/dashboard');
      } else {
        toast({
          title: 'Login failed',
          description: response.message || "Invalid login",
          status: 'error',
          duration: 3000,
          isClosable: true,
          position: 'top'
        });
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.message || 'Unexpected error.',
        status: 'error',
        duration: 3000,
        isClosable: true,
        position: 'top'
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
          <Box
            as='a'
            href={'/'}
          >
            <Image src={Logo} alt='SmartSpend' h='60px' />
          </Box>
          <Heading fontSize={"4xl"}>Sign in to your account</Heading>
          <Text fontSize={"lg"} color={"gray.600"} w={"max-content"}>
            to enjoy all of our cool{" "}
            <span className="text-primary-400">features</span> ✌️
          </Text>
        </Stack>
        <Box
          rounded={"lg"}
          bg={useColorModeValue("white", "gray.700")}
          boxShadow={"lg"}
          p={8}
        >
          <Stack spacing={4}>
            <form onSubmit={handleSubmit}>
              <FormControl id="email">
                <FormLabel>Email address</FormLabel>
                <Input
                  type="email"
                  focusBorderColor="primary.400"
                  value={credentials.email}
                  onChange={handleChange}
                />
              </FormControl>
              <FormControl id="password">
                <FormLabel>Password</FormLabel>
                {/* <Input type="password" focusBorderColor="primary.400"/> */}
                <InputGroup>
                  <Input
                    type={showPassword ? "text" : "password"}
                    focusBorderColor="primary.400"
                    value={credentials.password}
                    onChange={handleChange}
                  />
                  <InputRightElement h={"full"}>
                    <Button
                      variant={"ghost"}
                      onClick={() =>
                        setShowPassword((showPassword) => !showPassword)
                      }
                    >
                      {showPassword ? <ViewIcon /> : <ViewOffIcon />}
                    </Button>
                  </InputRightElement>
                </InputGroup>
              </FormControl>
              <Stack spacing={10}>
                <Stack
                  direction={{ base: "column", sm: "row" }}
                  align={"start"}
                  justify={"space-between"}
                >
                  <Checkbox
                    colorScheme="primary"
                    defaultChecked={false}
                    color="gray.700"
                  >
                    Remember me
                  </Checkbox>
                  <ChakraLink
                    as={Link}
                    to="/reset-email"
                    _hover={{ color: "primary.500" }}
                    color="primary.400"
                  >
                    Forgot password?
                  </ChakraLink>
                </Stack>
                <Button
                  type="submit"
                  size="lg"
                  bg={"primary.400"}
                  color={"white"}
                  _hover={{ bg: "primary.500" }}
                  isLoading={loading}
                  loadingText="Submitting"
                >
                  Login
                </Button>
              </Stack>
            </form>
            <Stack pt={6}>
              <Text align={"center"}>
                Don't have an account?{" "}
                <ChakraLink
                  as={Link}
                  to="/register"
                  _hover={{ color: "primary.500" }}
                  color="primary.400"
                >
                  Register
                </ChakraLink>
              </Text>
            </Stack>
          </Stack>
        </Box>
      </Stack>
    </Flex>
  );
}
