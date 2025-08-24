/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Button,
  Badge,
  Select,
  useToast,
} from "@chakra-ui/react";
import { useEffect, useRef, useState, useCallback } from "react";
import { getNotifications, markAllNotificationsRead } from "../../../services/notificationServices";
import Dash from "../../../components/loader/dashboard";

export default function NotificationsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [_page, setPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [filter, setFilter] = useState<string>("");
  const [total, setTotal] = useState<number>(0);
  const sentinelRef = useRef<HTMLDivElement | null>(null);
  const toast = useToast();

  const loadPage = useCallback(
    async (pageToLoad: number, filterType?: string, replace = false) => {
      setLoading(true);
      try {
        const data = await getNotifications(pageToLoad, filterType || undefined);
        setTotal(data.count);
        setHasMore(Boolean(data.next));

        setItems((prev) => {
          if (replace) return data.results;
          const existing = new Set(prev.map((i) => i.id));
          const merged = [...prev];
          for (const it of data.results) {
            if (!existing.has(it.id)) merged.push(it);
          }
          return merged;
        });
      } catch (e) {
        console.error(e);
        toast({
          title: "Failed to load notifications",
          status: "error",
          duration: 3000,
          isClosable: true,
          position: "top",
        });
      } finally {
        setLoading(false);
      }
    },
    [toast]
  );

  // initial load & filter change
  useEffect(() => {
    setPage(1);
    setItems([]);
    setHasMore(true);
    loadPage(1, filter || undefined, true);
  }, [filter, loadPage]);

  // infinite scroll observer
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
  }, [loading, hasMore, filter, loadPage]);

  const markAllRead = async () => {
    try {
      await markAllNotificationsRead();
      setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
      toast({
        title: "All notifications marked as read",
        status: "success",
        position: "top",
        duration: 3000,
      });
    } catch {
      toast({
        title: "Failed to mark all read",
        status: "error",
        position: "top",
        duration: 3000,
      });
    }
  };

  return (
    <Box p={6}>
      <HStack justify="space-between" mb={4} align="center">
        <Heading size="lg">Notifications</Heading>
        <HStack>
          <Select
            w="220px"
            placeholder="All types"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="spot_available">Spot Available</option>
            <option value="booking_reminder">Booking Reminder</option>
            <option value="general">General</option>
          </Select>
          <Button size="sm" colorScheme="blue" onClick={markAllRead}>
            Mark all as read
          </Button>
        </HStack>
      </HStack>

      <Text mb={2} color="gray.600">
        Showing {items.length} of {total}
      </Text>

      <VStack align="stretch" spacing={3}>
        {items.map((n) => (
          <Box
            key={n.id}
            p={4}
            borderWidth="1px"
            borderRadius="lg"
            bg={n.is_read ? "gray.50" : "blue.50"}
          >
            <HStack justify="space-between">
              <Heading size="sm">{n.title}</Heading>
              <Badge
                colorScheme={
                  n.type === "general"
                    ? "green"
                    : n.type === "booking_reminder"
                    ? "purple"
                    : "blue"
                }
              >
                {n.type}
              </Badge>
            </HStack>
            <Text fontSize="sm" color="gray.600">
              {new Date(n.sent_at).toLocaleString()}
            </Text>
            <Text mt={2}>{n.body}</Text>
          </Box>
        ))}

        {/* Sentinel for infinite scroll */}
        <div ref={sentinelRef} />

        {loading && <Dash />}

        {!loading && !hasMore && items.length === 0 && (
          <Box p={6} textAlign="center" color="gray.500">
            No notifications found.
          </Box>
        )}
      </VStack>
    </Box>
  );
}
