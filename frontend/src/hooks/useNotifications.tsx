import { useEffect, useState, useRef, useCallback } from "react";
import Cookies from "js-cookie";
import {
  unreadCount as fetchUnreadCount,
  getNotifications,
  getNotificationTypes,
  markAllNotificationsRead,
  markAsRead,
  markAsUnRead,
} from "../services/notificationServices";
import type {
  NotificationResponse,
  Notifications,
} from "../types/context/notification";
import { useToast } from "@chakra-ui/react";
// import { wsUrl } from "../services/constants";

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notifications[]>([]);
  const [notificationTypes, setNotificationTypes] = useState<string[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [filter, setFilter] = useState<string>("");
  const [total, setTotal] = useState<number>(0);
  const [noNotifications, setNoNotifications] = useState<boolean>(false);
  const sentinelRef = useRef<HTMLDivElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const toast = useToast();

  const refreshUnread = useCallback(async () => {
    try {
      const res = await fetchUnreadCount();
      setUnreadCount(res.unread ?? res);
    } catch (e) {
      console.error("Failed to fetch unread count:", e);
    }
  }, []);

  useEffect(() => {
    async function fetchTypes() {
      try {
        const types = await getNotificationTypes();
        setNotificationTypes(types);
      } catch (error) {
        console.error("Failed to fetch notification types:", error);
      }
    }
    fetchTypes();
  }, []);

  // load page of notifications
  const loadPage = useCallback(
    async (pageToLoad: number, filterType?: string, replace = false) => {
      try {
        const data: NotificationResponse = await getNotifications(
          pageToLoad,
          filterType
        );
        setTotal(data.count);
        setHasMore(Boolean(data.next));

        if (data.count === 0) {
          setNoNotifications(true);
        } else {
          setNoNotifications(false);
        }

        setNotifications((prev) => {
          if (replace) return data.results;
          const existing = new Set(prev.map((i) => i.id));
          const merged = [...prev];
          for (const it of data.results) {
            if (!existing.has(it.id)) merged.push(it);
          }
          return merged;
        });
        await refreshUnread();
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
    [toast, refreshUnread]
  );

  // reload when filter changes
  useEffect(() => {
    setPage(1);
    setNotifications([]);
    setHasMore(true);
    setNoNotifications(false);
    loadPage(1, filter, true);
  }, [filter, loadPage]);

  // mark all read
  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      await refreshUnread();
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

  // mark one read
  const handleMarkRead = async (id: number) => {
    try {
      await markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      await refreshUnread();
    } catch (e) {
      console.error("Failed to mark as read:", e);
    }
  };

  // mark one unread
  const handleMarkUnRead = async (id: number) => {
    try {
      await markAsUnRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: false } : n))
      );
      await refreshUnread();
    } catch (e) {
      console.error("Failed to mark as unread:", e);
    }
  };

  const handleToggleReadStatus = (id: number, isRead: boolean) => {
    if (isRead) {
      handleMarkUnRead(id);
    } else {
      handleMarkRead(id);
    }
  };
  
  // WebSocket
  useEffect(() => {
    const token = Cookies.get("token");
    if (!token) return;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrls = `${protocol}://localhost:8000/ws/notifications`;

    const ws = new WebSocket(`${wsUrls}/?token=${token}`);

    wsRef.current = ws;

    ws.onopen = () => {
      console.log("Connected to notifications WS");
    };

    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      console.log("📩 Incoming notification:", data);

      // backend sends { type: "...", data: {...} }
      if (data.type === "send_notification") {
        const notif: Notifications = data.data;
        setNotifications((prev) => [notif, ...prev]);
        await refreshUnread();
      }
      if (data.type === "unread_notifications") {
        setNotifications(data.notifications);
      }
    };

    ws.onclose = () => console.log("WS closed");
    ws.onerror = (err) => console.error("WS Error:", err);

    return () => {
      ws.close();
    };
  }, [refreshUnread]);

  return {
    notifications,
    unreadCount,
    setNotifications,
    total,
    hasMore,
    loading,
    page,
    sentinelRef,
    filter,
    noNotifications,
    notificationTypes,
    setFilter,
    setPage,
    loadPage,
    handleToggleReadStatus,
    handleMarkRead,
    handleMarkUnRead,
    handleMarkAllRead,
  };
};
