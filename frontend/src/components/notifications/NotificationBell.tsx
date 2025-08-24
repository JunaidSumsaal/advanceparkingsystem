import {
  Box,
  IconButton,
  Badge,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Text,
  MenuDivider,
} from "@chakra-ui/react";
import { BellIcon } from "@chakra-ui/icons";
import { useNotifications } from "../../hooks/useNotifications";
import { useEffect } from "react";

export default function NotificationBell() {
  const { notifications, unreadCount, loadPage, handleToggleReadStatus, handleMarkAllRead } = useNotifications();

  useEffect(() => {
    loadPage()
  }, [loadPage])

  return (
    <Menu>
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
      <MenuList maxH="300px" overflowY="auto">
        <MenuItem w={'full'} display={'flex'} justifyContent={'flex-end'}fontSize="xs" color="gray.500" textAlign={'center'} onClick={handleMarkAllRead}>Mark all as read</MenuItem>
        <MenuDivider />
        {notifications.length === 0 && <Text p={3}>No notifications</Text>}
        {notifications.map((n) => (
          <MenuItem
            key={n.id}
            onClick={() => handleToggleReadStatus(n.id, n.is_read)}
            style={{ opacity: n.is_read ? 0.5 : 1 }}
          >
            <Box>
              <Text fontWeight="bold">{n.title}</Text>
              <Text fontSize="sm">{n.body}</Text>
              <Text fontSize="xs" color="gray.500">
                {new Date(n.sent_at).toLocaleString()}
              </Text>
            </Box>
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  );
}
