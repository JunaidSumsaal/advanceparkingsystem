/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState, useEffect } from 'react';
import { Button, Input, FormControl, FormLabel, VStack, useToast } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../../context/AuthContext';

const Settings = () => {
  const { user, profilesUpdate } = useAuthContext();
  const [username, setUserName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const toast = useToast();
  const navigate = useNavigate();

  // Initialize form fields with current user info
  useEffect(() => {
    if (user) {
      setUserName(user.username || '');
      setEmail(user.email || '');
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  try {
    await profilesUpdate({ username, email, password: password || undefined });
    toast({
      title: "Profile updated",
      status: "success",
      duration: 5000,
      isClosable: true,
      position: 'top'
    });
    navigate('/dashboard');
  } catch (error: any) {
    toast({
      title: "Error updating profile",
      description: error.response?.data?.message || "Something went wrong.",
      status: "error",
      duration: 5000,
      isClosable: true,
      position: 'top'
    });
  }
};


  return (
    <VStack spacing={4} align="stretch" as="form" onSubmit={handleSubmit}>
      <FormControl id="username">
        <FormLabel>Username</FormLabel>
        <Input
          value={username}
          onChange={(e) => setUserName(e.target.value)}
          placeholder="Enter your username"
        />
      </FormControl>
      <FormControl id="email">
        <FormLabel>Email</FormLabel>
        <Input
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
        />
      </FormControl>
      <FormControl id="password">
        <FormLabel>Password</FormLabel>
        <Input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Change your password (optional)"
        />
      </FormControl>
      <Button colorScheme="blue" type="submit">
        Update Profile
      </Button>
    </VStack>
  );
};

export default Settings;
