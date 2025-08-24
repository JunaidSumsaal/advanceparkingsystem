import { useEffect, useState, useRef, useCallback } from "react";
import Cookies from "js-cookie";
import {
  unreadCount as fetchUnreadCount,
  getNotifications,
  markAllNotificationsRead,
  markAsRead,
  markAsUnRead,
} from "../services/notificationServices";
import type { NotificationResponse, Notifications } from "../types/context/notification";

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notifications[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // fetch page
  const loadPage = useCallback(
    async (pageToLoad = 1, replace = false) => {
      setLoading(true);
      try {
        const data: NotificationResponse = await getNotifications(pageToLoad);
        setTotal(data.count);
        setHasMore(Boolean(data.next));

        setNotifications((prev) => {
          if (replace) return data.results;
          const existing = new Set(prev.map((i) => i.id));
          const merged = [...prev];
          for (const it of data.results) {
            if (!existing.has(it.id)) merged.push(it);
          }
          return merged;
        });

        setUnreadCount(
          data.results.filter((n: Notifications) => !n.is_read).length +
            (pageToLoad === 1 ? 0 : unreadCount)
        );
      } finally {
        setLoading(false);
      }
    },
    [unreadCount]
  );

  // mark single read
  const handleMarkRead = async (id: number) => {
    await markAsRead(id);
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    );
    setUnreadCount((prev) => Math.max(prev - 1, 0));
  };

  const handleMarkUnRead = async (id: number) => {
    try {
      await markAsUnRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: false } : n))
      );
      setUnreadCount((prev) => Math.max(prev + 1, 0));
      console.log('unread');
    } catch (e) {
      console.error("Failed to mark as unread:", e);
    }
  };

  // handle toggle between read/unread
  const handleToggleReadStatus = (id: number, isRead: boolean) => {
    if (isRead) {
      handleMarkUnRead(id);
    } else {
      handleMarkRead(id);
    }
  };

  // mark all read
  const handleMarkAllRead = async () => {
    await markAllNotificationsRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    setUnreadCount(0);
  };

  useEffect(() => {
    const token = Cookies.get("access");
    if (!token) return;

    // initial unread count sync
    fetchUnreadCount().then(setUnreadCount);

    const wsUrl = "wss://advancepackingsystem-backend.onrender.com/ws/notifications/";
    const socket = new WebSocket(`${wsUrl}?token=${token}`);

    wsRef.current = socket;

    socket.onopen = () => console.log("Connected to notifications WS");

    socket.onmessage = (event) => {
      const data: Notifications = JSON.parse(event.data);

      if (data.id) {
        setNotifications((prev) => [data, ...prev]);
        setUnreadCount((prev) => prev + 1);
      }
    };

    socket.onclose = () => {
      console.log("WS closed, retrying…");
      setTimeout(() => window.location.reload(), 5000);
    };

    return () => socket.close();
  }, []);

  const markAllRead = () => setUnreadCount(0);

  return {
    notifications,
    unreadCount,
    setUnreadCount,
    setNotifications,
    markAllRead,
    total,
    hasMore,
    loading,
    page,
    setPage,
    loadPage,
    handleToggleReadStatus,
    handleMarkRead,
    handleMarkUnRead,
    handleMarkAllRead,
  };
};
