import {
  Box,
  Container,
  Image,
  useColorModeValue,
  Heading
} from '@chakra-ui/react';
import { motion } from 'framer-motion';
import Logo from '@assets/header_logo.png';
import { keyframes } from '@emotion/react';

const animationKeyframes = keyframes`
  0% { transform: scale(1) rotate(0); border-radius: 20%; }
  25% { transform: scale(2) rotate(0); border-radius: 20%; }
  50% { transform: scale(2) rotate(270deg); border-radius: 50%; }
  75% { transform: scale(1) rotate(270deg); border-radius: 50%; }
  100% { transform: scale(1) rotate(0); border-radius: 20%; }
`;

const animation = `${animationKeyframes} 2s ease-in-out infinite`;

export default function LoaderDash () {
  return (
    <>
      <Container
        minH='100vh'
        display='flex'
        alignItems='center'
        justifyContent='center'
        flexDirection='column'
      >
        <Box
          as={motion.div}
          animation={animation}
          padding='2'
          width='14'
          height='14'
          display='flex'
        >
          <Image src={Logo} width='100%' height='100%' />
        </Box>
        <Heading
          size='md'
          mt={4}
          fontWeight='500'
          color={useColorModeValue('gray.600', 'gray.400')}
        >
          We&apos;re getting everything ready for you...
        </Heading>
      </Container>
    </>
  );
}
