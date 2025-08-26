import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Button,
  Badge,
  Select,
} from "@chakra-ui/react";
import Dash from "../../../components/loader/dashboard";
import { useNotifications } from "../../../hooks/useNotifications";
import { formatSnakeCaseToTitleCase } from "../../../utils/capitilizer";
import { CircleQuestionMark } from "lucide-react";
import { useEffect } from "react";

export default function NotificationsPage() {
  const {
    handleToggleReadStatus,
    sentinelRef,
    loading,
    hasMore,
    total,
    notifications,
    handleMarkAllRead,
    filter,
    setFilter,
    noNotifications,
    notificationTypes,
    setPage,
    loadPage,
  } = useNotifications();

  useEffect(() => {
    if (!sentinelRef.current) return;
    const el = sentinelRef.current;

    const obs = new IntersectionObserver(
      (entries) => {
        const first = entries[0];
        if (first.isIntersecting && !loading && hasMore) {
          setPage((prevPage) => {
            const nextPage = prevPage + 1;
            loadPage(nextPage, filter || undefined);
            return nextPage;
          });
        }
      },
      { rootMargin: "200px" }
    );

    obs.observe(el);
    return () => obs.unobserve(el);
  }, [loading, hasMore, filter, loadPage, sentinelRef, setPage]);
  return (
    <Box p={6}>
      <HStack justify="space-between" mb={4} align="center" flexWrap={"wrap"}>
        <Heading size="lg">Notifications</Heading>
        <HStack
          justify="space-between"
          className="md:flex flex-wrap md:flex-nowrap"
        >
          <Select
            w="220px"
            placeholder="All types"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            {notificationTypes.map((type) => (
              <option key={type} value={type}>
                {formatSnakeCaseToTitleCase(type)}
              </option>
            ))}
          </Select>
          <Button
            size="sm"
            bg="primary.400"
            color={"white"}
            onClick={handleMarkAllRead}
          >
            Mark all as read
          </Button>
        </HStack>
      </HStack>

      <Text mb={2} color="gray.600">
        Showing {notifications.length} of {total}
      </Text>

      {noNotifications && filter && (
        <Box
          p={6}
          textAlign="center"
          color="gray.500"
          display={"flex"}
          flexDirection={"column"}
          justifyContent={"center"}
        >
          <CircleQuestionMark />
          No notifications available for {formatSnakeCaseToTitleCase(filter)}.
        </Box>
      )}

      <VStack align="stretch" spacing={3}>
        {notifications.map((n) => (
          <Box
            as="button"
            key={n.id}
            p={4}
            borderWidth="1px"
            borderRadius="lg"
            borderLeft={n.is_read ? "none" : "4px"}
            borderLeftColor={n.is_read ? "gray.50" : "blue.200"}
            bg={n.is_read ? "gray.50" : "blue.50"}
            onClick={() => handleToggleReadStatus(n.id, n.is_read)}
            _hover={{ bg: "secondary.50" }}
          >
            <HStack justify="space-between">
              <Heading size="sm">{n.title}</Heading>
              <Badge
                colorScheme={
                  n.type === "general"
                    ? "green"
                    : n.type === "booking_reminder"
                    ? "purple"
                    : n.type === "spot_available"
                    ? "orange"
                    : "white"
                }
                p={2}
              >
                {n.type}
              </Badge>
            </HStack>
            <Text mt={2}>{n.body}</Text>
            <Text fontSize="sm" color="gray.600">
              {new Date(n.sent_at).toLocaleString()}
            </Text>
          </Box>
        ))}

        {/* Sentinel for infinite scroll */}
        <div ref={sentinelRef} />

        {loading && <Dash />}

        {!loading && !hasMore && noNotifications && !filter && (
          <Box p={6} textAlign="center" color="gray.500">
            No notifications found.
          </Box>
        )}
      </VStack>
    </Box>
  );
}
