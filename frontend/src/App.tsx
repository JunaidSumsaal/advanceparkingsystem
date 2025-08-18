import { ColorModeScript, ChakraProvider } from '@chakra-ui/react';
import { Router } from './routes';
import { theme } from './utils/theme';
import './index.css';
import { AuthProvider } from './context/AuthContext';
import { UserProvider } from './context/UsersContext';

export default function App() {
  return (
    <>
      <ColorModeScript />
      <ChakraProvider theme={theme}>
        <AuthProvider>
          <UserProvider>
            <Router />
          </UserProvider>
        </AuthProvider>
      </ChakraProvider>
    </>
  );
}
