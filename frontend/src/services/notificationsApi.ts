/* eslint-disable @typescript-eslint/no-explicit-any */
import apiHelper from "../utils/apiHelper";
import {
  NOTIFICATIONS,
  NOTIF_LIST,
  NOTIF_HISTORY,
  NOTIF_EMAIL_PREF,
  NOTIF_SUBSCRIBE,
  NOTIF_UNSUBSCRIBE,
  NOTIF_PUSH,
} from "./constants";

// Notifications
export const getNotifications = async () => {
  const res = await apiHelper.get(`${NOTIFICATIONS}${NOTIF_LIST}/`);
  return res.data;
};

export const getNotification = async (id: number) => {
  const res = await apiHelper.get(`${NOTIFICATIONS}${NOTIF_LIST}/${id}/`);
  return res.data;
};

export const markNotificationRead = async (id: number) => {
  const res = await apiHelper.post(`${NOTIFICATIONS}${NOTIF_LIST}/${id}/read/`);
  return res.data;
};

export const markAllNotificationsRead = async () => {
  const res = await apiHelper.post(`${NOTIFICATIONS}/mark_all_read/`);
  return res.data;
};

export const getUnreadCount = async () => {
  const res = await apiHelper.get(`${NOTIFICATIONS}/unread_count/`);
  return res.data;
};

export const getNotificationHistory = async (params?: any) => {
  const res = await apiHelper.get(`${NOTIFICATIONS}${NOTIF_HISTORY}/`, {
    params,
  });
  return res.data;
};

// Email Preferences
export const updateEmailPreference = async (data: {
  email_notifications: boolean;
}) => {
  const res = await apiHelper.patch(
    `${NOTIFICATIONS}${NOTIF_EMAIL_PREF}/`,
    data
  );
  return res.data;
};

// Push Subscriptions
export const getPushSubscriptions = async (params?: any) => {
  const res = await apiHelper.get(`${NOTIFICATIONS}${NOTIF_PUSH}/`, { params });
  return res.data;
};

export const createPushSubscription = async (data: any) => {
  const res = await apiHelper.post(`${NOTIFICATIONS}${NOTIF_SUBSCRIBE}/`, data);
  return res.data;
};

export const unsubscribePush = async (data: any) => {
  const res = await apiHelper.post(
    `${NOTIFICATIONS}${NOTIF_UNSUBSCRIBE}/`,
    data
  );
  return res.data;
};
