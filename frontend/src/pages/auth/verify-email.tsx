import { Box, Button, Flex, Image } from '@chakra-ui/react';
import Logo from '@assets/header_logo.png';
import { Link } from 'react-router-dom';


export default function VerifyEmail () {
  return (
    <>
      <Flex
        justify='center'
        align='center'
        h='100vh'
        w='100%'
        position='relative'
        className='flex flex-col text-center gap-4'
      >
        <Box
          as='a'
          href='/'
        >
          <Image src={Logo} alt='SmartSpend' h='60px' />
        </Box>
        <Box>
          <h1>Verify Email</h1>
          <p>Check your email for a link to verify your email address.</p>
        </Box>
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
      </Flex>
    </>
  );
};
