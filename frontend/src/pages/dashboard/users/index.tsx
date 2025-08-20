import React from 'react';
import { Box, Table, Thead, Tbody, Tr, Th, Td, Button, Tooltip, useDisclosure, Text } from '@chakra-ui/react';
import type { User } from '../../../types/User';
import Pagination from '../../../components/dashboard/pagination';
import { useAdminUsers } from '../../../hooks/useAdminUsers';

const Users = () => {
  const { users, currentPage, totalPages, setCurrentPage } = useAdminUsers();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedUser, setSelectedUser] = React.useState<User | null>(null);
  const [totalUsers] = React.useState(users.length);

  const handleUserClick = (user: User) => {
    setSelectedUser(user);
    onOpen();
  };

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <Box p={5} bg={'white'}>
      {/* Pagination Controls */}
      <Box mb={4} textAlign="center" display={'flex'} justifyContent={'space-between'} alignItems={'center'} mx={4}>
        <Pagination currentPage={currentPage} totalPages={totalPages} handlePageChange={handlePageChange} />
        <Text color={'gray.400'} fontSize={'md'}>
          {totalUsers} Total Users
        </Text>
      </Box>
      <Table variant="simple" colorScheme="primary">
        <Thead className="text-xs text-white uppercase bg-gray-50 dark:bg-gray-700 dark:text-white">
          <Tr>
            <Th className="px-6 py-3">User Name</Th>
            <Th className="px-6 py-3">Email</Th>
            <Th className="px-6 py-3">Role</Th>
            <Th className="px-6 py-3">Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {users.map((user: User) => (
            <Tr key={user.id} className="odd:bg-white odd:dark:bg-gray-900 even:bg-gray-50 even:dark:bg-gray-800 border-b dark:border-gray-700 border-gray-200">
              <Td className="px-6 py-2 font-medium text-gray-900 whitespace-nowrap dark:text-white">{user.username}</Td>
              <Td className="px-6 py-2 text-gray-900 whitespace-nowrap dark:text-white">{user.email}</Td>
              <Td className="px-6 py-2 text-gray-900 whitespace-nowrap dark:text-white">{user.role ? 'Admin' : 'Standard'}</Td>
              <Td className="px-6 py-2 text-gray-900 whitespace-nowrap dark:text-white">
                <Tooltip label="View Details" hasArrow>
                  <Button onClick={() => handleUserClick(user)} colorScheme="blue" variant="link">View</Button>
                </Tooltip>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>


      {/* Popup to view user details */}
      {isOpen && selectedUser && (
        <Box p={5} boxShadow="lg" borderRadius="md" bg="white" position="absolute" top="50%" left="50%" transform="translate(-50%, -50%)">
          <h2>User Details</h2>
          <p>Name: {selectedUser.username}</p>
          <p>Email: {selectedUser.email}</p>
          <p>Role: {selectedUser.role ? 'Admin' : 'Standard'}</p>
          <Button mt={4} onClick={onClose}>Close</Button>
        </Box>
      )}
    </Box>
  );
};

export default Users;
