/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState } from 'react';
import { Button, Input, FormControl, FormLabel, VStack, useToast } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { updateProfile } from '../../../services/authService';
import { useAuth } from '../../../context/AuthContext';

const Settings = () => {
  const { user } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [password, setPassword] = useState('');
  const toast = useToast();
  const history = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await updateProfile({ name, email, password });
      toast({
        title: "Profile updated",
        status: "success",
        duration: 5000,
        isClosable: true,
        position: 'top'
      });
      history('/dashboard');
    } catch (error: any) {
      toast({
        title: "Error updating profile",
        description: error.response?.data?.message || "Something went wrong while updating your profile.",
        status: "error",
        duration: 5000,
        isClosable: true,
        position: 'top'
      });
    }
  };

  return (
    <VStack spacing={4} align="stretch">
      <FormControl id="name">
        <FormLabel>Name</FormLabel>
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name"
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
      <Button colorScheme="blue" onClick={handleSubmit}>
        Update Profile
      </Button>
    </VStack>
  );
};

export default Settings;
