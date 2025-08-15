import { useState, useEffect } from 'react';
import {
  Button,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Stack,
  useColorModeValue,
  useToast,
  Image,
  Box,
} from '@chakra-ui/react';
import { useNavigate, useSearchParams, Link as RouterLink } from 'react-router-dom';
import Logo from '../../assets/header_logo.png';
import { resetPassword } from '../../services/authService';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      toast({
        title: 'Invalid link',
        description: 'No reset token provided.',
        status: 'error',
        duration: 5000,
        isClosable: true,
        position: 'top'
      });
      navigate('/forgot-password');
    }
  }, [token, navigate, toast]);

  const handleSubmit = async () => {
    if (password !== confirm) {
      toast({
        title: "Passwords don't match",
        status: 'error',
        duration: 3000,
        isClosable: true,
        position: 'top'
      });
      return;
    }
    setLoading(true);
    try {
      const res = await resetPassword(token, password);
      toast({
        title: 'Password reset!',
        description: res.message || 'You can now log in with your new password.',
        status: 'success',
        duration: 3000,
        isClosable: true,
        position: 'top'
      });
      navigate('/login');
    } catch (err: any) {
      toast({
        title: 'Error',
        description: err.response?.data?.message || 'Failed to reset password.',
        status: 'error',
        duration: 5000,
        isClosable: true,
        position: 'top'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex
      minH="100vh"
      align="center"
      justify="center"
      bg={useColorModeValue('gray.50', 'gray.800')}
    >
      <Stack
        spacing={4}
        w="full"
        maxW="md"
        bg={useColorModeValue('white', 'gray.700')}
        rounded="xl"
        boxShadow="lg"
        p={6}
        my={12}
      >
        <Box as={RouterLink} to="/" textAlign="center">
          <Image src={Logo} alt="SmartSpend" h="60px" mx="auto" />
        </Box>

        <Heading lineHeight={1.1} fontSize={{ base: '2xl', md: '3xl' }} textAlign="center">
          Enter new password
        </Heading>

        <FormControl id="password" isRequired>
          <FormLabel>New Password</FormLabel>
          <Input
            type="password"
            focusBorderColor="primary.400"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </FormControl>

        <FormControl id="confirm" isRequired>
          <FormLabel>Confirm Password</FormLabel>
          <Input
            type="password"
            focusBorderColor="primary.400"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
          />
        </FormControl>

        <Stack spacing={6}>
          <Button
            bg="primary.400"
            color="white"
            _hover={{ bg: 'primary.500' }}
            onClick={handleSubmit}
            isLoading={loading}
            loadingText="Submitting"
          >
            Submit
          </Button>
          <Button
            variant="link"
            as={RouterLink}
            to="/login"
            alignSelf="center"
          >
            Back to Login
          </Button>
        </Stack>
      </Stack>
    </Flex>
  );
}
