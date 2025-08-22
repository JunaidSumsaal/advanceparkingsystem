import { Box, Heading, Text, Button } from '@chakra-ui/react';
import { Link } from 'react-router-dom';

export const Error404 = () => {
  return (
    <Box
      py={10}
      px={6}
      w='full'
      minH='100vh'
      display='flex'
      flexDirection='column'
      alignItems='center'
      justifyContent='center'
    >
      <Heading
        display='inline-block'
        as='h2'
        size='2xl'
        bgGradient='linear(to-r, orange.400, orange.600)'
        backgroundClip='text'
      >
        401
      </Heading>
      <Text fontSize='18px' mt={3} mb={2}>
        Unauthorized request
      </Text>
      <Text color='gray.500' mb={6}>
        The do not have access to th page you&apos;re looking for
      </Text>

      <Button
        colorScheme='orange'
        bgGradient='linear(to-r, orange.400, orange.500, orange.600)'
        color='white'
        variant='solid'
      >
        <Link to='/'>
          Go to Home
        </Link>
      </Button>
    </Box>
  );
};
