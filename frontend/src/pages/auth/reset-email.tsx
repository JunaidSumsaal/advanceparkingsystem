import {
  Button,
  FormControl,
  Flex,
  Heading,
  Input,
  Stack,
  Text,
  useColorModeValue,
  Image,
  Box,
  useToast
} from '@chakra-ui/react';
import Logo from '@assets/header_logo.png';
import { forgotPassword } from '@services/authService';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function RestEmail () {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!email) {
      toast({
        title: "Email required",
        status: "error",
        duration: 3000,
        isClosable: true,
        position: 'top'
      });
      return;
    }
    setLoading(true);
    try {
      const response = await forgotPassword(email);
      toast({
        title: "Reset email sent!",
        description: response.message || "Check your inbox.",
        status: "success",
        duration: 3000,
        isClosable: true,
        position: 'top'
      });
      navigate('/verify-email')
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Something went wrong.",
        status: "error",
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
      minH='100vh'
      align='center'
      justify='center'
      bg={useColorModeValue('gray.50', 'gray.800')}
    >
      <Stack
        spacing={4}
        w='full'
        maxW='md'
        bg={useColorModeValue('white', 'gray.700')}
        rounded='xl'
        boxShadow='lg'
        p={6}
        my={12}
      >
        <Box
          as='a'
          href='/'
          w='full'
          className='flex justify-center items-center'
        >
          <Image src={Logo} alt='SmartSpend' h='60px' />
        </Box>
        <Heading lineHeight={1.1} fontSize={{ base: '2xl', md: '3xl' }}>
          Forgot your password?
        </Heading>
        <Text
          fontSize={{ base: 'sm', sm: 'md' }}
          color={useColorModeValue('gray.800', 'gray.400')}
        >
          You&apos;ll get an email with a reset link
        </Text>
        <FormControl id='email'>
          <Input
            placeholder='your-email@example.com'
            _placeholder={{ color: 'gray.500' }}
            type='email'
            focusBorderColor='primary.400'
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </FormControl>
        <Stack spacing={6}>
          <Button
            bg='primary.400'
            color='white'
            _hover={{
              bg: 'primary.500'
            }}
            onClick={handleSubmit}
            isLoading={loading}
            loadingText="Requesting"
          >
            Request Reset
          </Button>
        </Stack>
      </Stack>
    </Flex>
  );
}
