import React, { createContext, useContext, useState, useCallback } from "react";
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
  getUnreadCount,
  updateEmailPreference as apiUpdateEmailPreference,
  createPushSubscription,
  unsubscribePush,
} from "../services/notificationsApi";
import type {
  NotificationsContextType,
  Notification,
  PushSubscription,
  EmailPreference,
  NotificationPreference,
  NotificationTemplate,
} from "../types/context/notification";

const NotificationsContext = createContext<NotificationsContextType | undefined>(undefined);

export const NotificationsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [pushSubscriptions, setPushSubscriptions] = useState<PushSubscription[]>([]);
  const [emailPreference, setEmailPreference] = useState<EmailPreference | null>(null);
  const [notificationPreference, setNotificationPreference] = useState<NotificationPreference | null>(null);
  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /** Notifications */
  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getNotifications();
      setNotifications(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch notifications");
    } finally {
      setLoading(false);
    }
  }, []);

  const markRead = useCallback(async (id: number) => {
    await markNotificationRead(id);
    await fetchNotifications();
  }, [fetchNotifications]);

  const markAllRead = useCallback(async () => {
    await markAllNotificationsRead();
    await fetchNotifications();
  }, [fetchNotifications]);

  const fetchUnreadCount = useCallback(async () => {
    try {
      const res = await getUnreadCount();
      setUnreadCount(res.count);
    } catch (err) {
      console.error(err);
      throw err;
    }
  }, []);

  /** Preferences */
  const updateEmailPref = useCallback(async (receiveEmails: boolean) => {
    try {
      await apiUpdateEmailPreference({ email_notifications: receiveEmails });
      setEmailPreference(prev => prev ? { ...prev, receive_emails: receiveEmails } : { id: 0, user: 0, receive_emails: receiveEmails });
    } catch (err) {
      console.error(err);
      throw err;
    }
  }, []);

  /** Push Subscriptions */
  const addPushSubscription = useCallback(createPushSubscription, []);
  const removePushSubscription = useCallback(unsubscribePush, []);

  return (
    <NotificationsContext.Provider
      value={{
        notifications,
        pushSubscriptions,
        emailPreference,
        notificationPreference,
        templates,
        unreadCount,
        fetchNotifications,
        markRead,
        markAllRead,
        fetchUnreadCount,
        updateEmailPreference: updateEmailPref,
        addPushSubscription,
        removePushSubscription,
        loading,
        error,
        setError,
        setLoading,
        setNotifications,
        setPushSubscriptions,
        setEmailPreference,
        setNotificationPreference,
        setTemplates,
      }}
    >
      {children}
    </NotificationsContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useNotificationsContext = () => {
  const ctx = useContext(NotificationsContext);
  if (!ctx) throw new Error("useNotificationsContext must be used within NotificationsProvider");
  return ctx;
};


