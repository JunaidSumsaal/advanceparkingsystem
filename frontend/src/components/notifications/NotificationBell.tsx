import {
  Box,
  IconButton,
  Badge,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Text,
  MenuDivider,
  Button,
  useDisclosure,
} from "@chakra-ui/react";
import { BellIcon } from "@chakra-ui/icons";
import { useNotifications } from "../../hooks/useNotifications";
import { CircleCheck } from "lucide-react";

export default function NotificationBell() {
  const {
    notifications,
    unreadCount,
    noNotifications,
    handleToggleReadStatus,
    handleMarkAllRead,
  } = useNotifications();
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <Menu isOpen={isOpen} onOpen={onOpen} onClose={onClose}>
      <MenuButton
        as={IconButton}
        icon={
          <Box position="relative">
            <BellIcon boxSize={6} />
            {unreadCount > 0 && (
              <Badge
                position="absolute"
                top="-1"
                right="-1"
                colorScheme="red"
                rounded="full"
                fontSize="0.7em"
              >
                {unreadCount}
              </Badge>
            )}
          </Box>
        }
        variant="ghost"
      />
      <MenuList maxH="300px" overflowY="auto" p={0}>
        <Box
          w="full"
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          p={3}
        >
          <Text fontWeight="bold">Notifications</Text>
          <Button
            size="sm"
            variant="ghost"
            fontSize="xs"
            onClick={handleMarkAllRead}
            isDisabled={unreadCount === 0}
            leftIcon={<CircleCheck size={14} />}
            _hover={{ bg: "gray.100" }}
          >
            Mark all as read
          </Button>
        </Box>
        <MenuDivider mt={0} />

        {noNotifications ? (
          <Text p={4} textAlign="center" color="gray.500">
            No notifications available.
          </Text>
        ) : (
          notifications.map((n) => (
            <MenuItem
              key={n.id}
              onClick={() => handleToggleReadStatus(n.id, n.is_read)}
              _hover={{ bg: n.is_read ? "gray.100" : "blue.100" }}
              bg={n.is_read ? "gray.50" : "blue.50"}
            >
              <Box>
                <Text fontWeight="bold">{n.title}</Text>
                <Text fontSize="sm">{n.body}</Text>
                <Text fontSize="xs" color="gray.500">
                  {new Date(n.sent_at).toLocaleString()}
                </Text>
              </Box>
            </MenuItem>
          ))
        )}
      </MenuList>
    </Menu>
  );
}
