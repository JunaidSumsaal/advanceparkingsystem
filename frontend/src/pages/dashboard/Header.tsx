import {
  IconButton,
  Avatar,
  HStack,
  VStack,
  useColorModeValue,
  Text,
  Menu,
  MenuButton,
  MenuDivider,
  MenuItem,
  MenuList,
  useDisclosure,
  Flex,
  Box,
  useToast,
  Image,
Link as ChakraLink,
} from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Logo from '../../assets/header_logo.png';
import { FiMenu, FiChevronDown } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const [userName, setUserName] = useState('');
  const [email, setEmail] = useState('');
  const [admin, setAdmin] = useState(false);
  const { onOpen } = useDisclosure();
  const toast = useToast();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      setUserName(user.name);
      setAdmin(user.isAdmin);
      setEmail(user.email);
    }
  }, [user]);

  const handleLogout = async () => {
    try {
      await logout();
      toast({
        title: 'Good Bye ✌️',
        description: 'Comeback again',
        status: "success",
        duration: 5000,
        isClosable: true,
        position: 'top'
      });
      navigate('/login')
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <Flex
      ml={{ base: 0, md: 60 }}
      px={{ base: 4, md: 4 }}
      height="20"
      alignItems="center"
      bg={useColorModeValue('white', 'gray.900')}
      borderBottomWidth="1px"
      borderBottomColor={useColorModeValue('gray.200', 'gray.700')}
      justifyContent={{ base: 'space-between', md: 'flex-end' }}
      top={0}
      right={0}
      position={'fixed'}
      w={'full'}
      zIndex={9}
    >
      <IconButton
        display={{ base: 'flex', md: 'none' }}
        onClick={onOpen}
        variant="outline"
        aria-label="open menu"
        icon={<FiMenu />}
      />
      <Text as="h2" display={{ base: 'flex', md: 'none' }} fontSize="xl" fontFamily="monospace" fontWeight="bold" className="flex gap-2" color={'primary.300'}>
        <Image src={Logo} alt='SmartSpend' h='30px' />
        SmartSpend
      </Text>
      <HStack spacing={{ base: '0', md: '6' }}>
        {/* <IconButton size="lg" variant="ghost" aria-label="open menu" icon={<FiBell />} /> */}
        <Flex alignItems={'center'}>
          <Menu>
            <MenuButton py={2} transition="all 0.3s" _focus={{ boxShadow: 'none' }}>
              <HStack>
                <Avatar
                  size={'sm'}
                  src={`https://ui-avatars.com/api/?format=svg&name=${userName}&bold=true&background=random&length=1&rounded=true`}
                />
                <VStack display={{ base: 'none', md: 'flex' }} alignItems="flex-start" spacing="1px" ml="2">
                  <Text fontSize="sm">{userName}</Text>
                  <Text fontSize="xs" color="gray.600">{admin ? 'Admin' : email}</Text>
                </VStack>
                <Box display={{ base: 'none', md: 'flex' }}>
                  <FiChevronDown />
                </Box>
              </HStack>
            </MenuButton>
            <MenuList bg={useColorModeValue('white', 'gray.900')} borderColor={useColorModeValue('gray.200', 'gray.700')}>
              <MenuItem>
                <ChakraLink
                  as={Link}
                  to="/dashboard/settings"
                  _hover={{ color: "primary.500" }}
                  color="primary.400"
                >
                  Settings
                </ChakraLink>
              </MenuItem>
              {admin && <MenuItem>
                <ChakraLink
                  as={Link}
                  to="/dashboard/users"
                  _hover={{ color: "primary.500" }}
                  color="primary.400"
                >
                  Users
                </ChakraLink>
              </MenuItem>}
              <MenuDivider />
              <MenuItem
                onClick={handleLogout}
              >
                Logout
              </MenuItem>
            </MenuList>
          </Menu>
        </Flex>
      </HStack>
    </Flex>
  );
};

export default Header;
