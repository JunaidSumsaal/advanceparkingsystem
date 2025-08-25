import { Outlet } from "react-router-dom";
import Sidebar from "./SideNav";
import { Box } from '@chakra-ui/react';

const Dashboard = () => {
  return (
    <Box minH="100vh" bg="gray.100" display={'flex'} w={'full'}>
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <Box w={'full'} ml={{ base: 0, md: 60 }} transition="margin-left 0.2s">

        {/* Page Content */}
        <Box p="6" pt="24"> {/* pt24 adds padding top to push content below Header */}
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
