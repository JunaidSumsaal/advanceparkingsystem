import {
  Box,
  CloseButton,
  Flex,
  Icon,
  useColorModeValue,
  Text,
  Drawer,
  DrawerContent,
  useDisclosure,
  IconButton,
  Image,
} from "@chakra-ui/react";
import {
  BarChart3,
  LayoutDashboard,
  User,
  Settings,
  Bell,
  MapPin,
  BookCheckIcon,
} from "lucide-react";
import type { BoxProps } from "@chakra-ui/react";
import { type IconType } from "react-icons";
import { useState } from "react";
import { FiHome } from "react-icons/fi";
import Logo from "../../assets/header_logo.png";
import { Link as RouterLink } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
interface SidebarProps extends BoxProps {
  onClose: () => void;
}

const LinkItems: Array<{
  name: string;
  icon: IconType;
  path: string;
  roles?: string[];
}> = [
  { name: "Dashboard",
    icon: LayoutDashboard,
    path: "/dashboard"
  },
  {
    name: "Metrics",
    icon: BarChart3,
    path: "/dashboard/metrics",
    roles: ["admin", "provider"],
  },
  {
    name: "Bookings",
    icon: BookCheckIcon,
    path: "/dashboard/booking",
    roles: ["admin", "provider", "attendant", "driver"],
  },
  {
    name: "Maps",
    icon: MapPin,
    path: "/dashboard/maps",
    roles: ["admin", "provider", "driver"],
  },
  {
    name: "Notifications",
    icon: Bell,
    path: "/dashboard/notifications",
    roles: ["admin", "provider", "attendant", "driver"],
  },
  {
    name: "Settings",
    icon: Settings,
    path: "/dashboard/settings",
    roles: ["admin", "provider", "attendant", "driver"],
  },
  { name: "Users",
    icon: User,
    path: "/dashboard/users",
    roles: ["admin"]
  },
];

const SidebarContent = ({
  onClose,
  activeLink,
  onLinkClick,
  ...rest
}: SidebarProps & {
  activeLink: string;
  onLinkClick: (name: string) => void;
}) => {
  const { user } = useAuth();


  return (
    <Box
      transition="3s ease"
      bg={useColorModeValue("white", "gray.900")}
      borderRight="1px"
      borderRightColor={useColorModeValue("gray.200", "gray.700")}
      w={{ base: "full", md: 60 }}
      pos="fixed"
      top={0}
      h="full"
      zIndex={10}
      {...rest}
    >
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Text
          as="h2"
          fontSize="xl"
          fontFamily="monospace"
          fontWeight="bold"
          className="flex gap-2"
          color={"primary.300"}
        >
          <Image src={Logo} alt="APS" h="30px" />
          APS
        </Text>
        <CloseButton display={{ base: "flex", md: "none" }} onClick={onClose} />
      </Flex>

      {LinkItems.filter(
        (link) => !link.roles || link.roles.includes(user?.role.toLowerCase() ?? "")
      ).map((link) => (
        <NavItem
          key={link.name}
          icon={link.icon}
          to={link.path}
          isActive={activeLink === link.name}
          onClick={() => onLinkClick(link.name)}
        >
          {link.name}
        </NavItem>
      ))}
    </Box>
  );
};

const NavItem = ({
  icon,
  children,
  isActive,
  to,
  onClick,
  ...rest
}: {
  icon: IconType;
  children: React.ReactNode;
  isActive: boolean;
  to: string;
  onClick: () => void;
}) => {
  return (
    <Box
      as={RouterLink}
      to={to}
      onClick={onClick}
      _hover={{ textDecoration: "none" }}
    >
      <Flex
        align="center"
        p="4"
        mx="4"
        my="1"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        _hover={{ bg: "primary.400", color: "white" }}
        bg={isActive ? "primary.400" : "transparent"}
        color={isActive ? "white" : "inherit"}
        {...rest}
      >
        {icon && (
          <Icon
            mr="4"
            fontSize="16"
            _groupHover={{ color: "white" }}
            as={icon}
          />
        )}
        {children}
      </Flex>
    </Box>
  );
};

const Sidebar = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [activeLink, setActiveLink] = useState<string>("Home");

  const handleLinkClick = (name: string) => {
    setActiveLink(name);
    onClose();
  };

  return (
    <Box minH="100vh" bg={useColorModeValue("gray.100", "gray.900")}>
      {/* For Desktop View */}
      <SidebarContent
        activeLink={activeLink}
        onLinkClick={handleLinkClick}
        onClose={onClose}
        display={{ base: "none", md: "block" }}
      />

      {/* Button to Open Sidebar on Mobile View */}
      <IconButton
        display={{ base: "flex", md: "none" }}
        aria-label="Open Sidebar"
        icon={<FiHome />}
        onClick={onOpen}
        position="fixed"
        top="4"
        left="4"
      />

      {/* Drawer for Mobile View */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="full">
        <DrawerContent>
          <SidebarContent
            activeLink={activeLink}
            onLinkClick={handleLinkClick}
            onClose={onClose}
          />
        </DrawerContent>
      </Drawer>
    </Box>
  );
};

export default Sidebar;
