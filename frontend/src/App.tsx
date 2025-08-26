import { ColorModeScript, ChakraProvider } from "@chakra-ui/react";
import { Router } from "./routes";
import { theme } from "./utils/theme";
import "./index.css";
import { AuthProvider } from "./context/AuthContext";
import { UserProvider } from "./context/UsersContext";
import { DashboardProvider } from "./context/DashboardContext";

const Providers = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>
      <DashboardProvider>
        <UserProvider>
          {children}
        </UserProvider>
      </DashboardProvider>
  </AuthProvider>
);

export default function App() {
  return (
    <>
      <ColorModeScript />
      <ChakraProvider theme={theme}>
        <Providers>
          <Router />
        </Providers>
      </ChakraProvider>
    </>
  );
}
