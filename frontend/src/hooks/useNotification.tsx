import { useNotificationsContext } from '../context/NotificationsContext';

export const useNotifications = () => {
  const {
    notifications,
    pushSubscriptions,
    unreadCount,
    fetchNotifications,
    markRead,
    markAllRead,
    fetchUnreadCount,
    addPushSubscription,
    removePushSubscription,
    loading,
    error,
    setError,
    setLoading,
  } = useNotificationsContext();

  return {
    notifications,
    pushSubscriptions,
    unreadCount,
    fetchNotifications,
    markRead,
    markAllRead,
    fetchUnreadCount,
    addPushSubscription,
    removePushSubscription,
    loading,
    error,
    setError,
    setLoading,
  };
};
