/* eslint-disable @typescript-eslint/no-explicit-any */
import type { NotificationResponse, Notifications } from "../types/context/notification";
import apiHelper from "../utils/apiHelper";
import {
  NOTIFICATIONS,
  NOTIF_LIST,
  NOTIF_HISTORY,
  NOTIF_EMAIL_PREF,
  NOTIF_UNSUBSCRIBE,
  NOTIF_PUSH,
} from "./constants";

// Notifications
export const getNotifications = async (page = 1, type?: string): Promise<NotificationResponse> => {
  let url = `${NOTIFICATIONS}${NOTIF_LIST}/?page=${page}`;
  if (type) url += `&type=${encodeURIComponent(type)}`;
  const res = await apiHelper.get(url);
  return res as NotificationResponse;
};

export const markAsRead = async (id: number) => {
  const res = await apiHelper.patch(`${NOTIFICATIONS}${NOTIF_LIST}/${id}/read/`, {});
  return res.data;
};

export const markAsUnRead = async (id: number) => {
  const res = await apiHelper.patch(`${NOTIFICATIONS}${NOTIF_LIST}/${id}/read/`, {});
  return res.data;
};


export const getNotification = async (id: number): Promise<Notifications>  => {
  const res = await apiHelper.get(`${NOTIFICATIONS}${NOTIF_LIST}/${id}/`);
  return res as Notifications;
};


export const markAllNotificationsRead = async () => {
  const res = await apiHelper.post(`${NOTIFICATIONS}${NOTIF_LIST}/mark_all_read/`);
  return res;
};

export const unreadCount = async () => {
  const res = await apiHelper.get(`${NOTIFICATIONS}${NOTIF_LIST}/unread_count/`);
  return res.unread;
};

export const getNotificationHistory = async (params?: any) => {
  const res = await apiHelper.get(`${NOTIFICATIONS}${NOTIF_HISTORY}/`, {
    params,
  });
  return res;
};

// Email Preferences
export const updateEmailPreference = async (data: {
  email_notifications: boolean;
}) => {
  const res = await apiHelper.patch(
    `${NOTIFICATIONS}${NOTIF_EMAIL_PREF}/`,
    data
  );
  return res;
};

// Push Subscriptions
export const getPushSubscriptions = async (params?: any) => {
  const res = await apiHelper.get(`${NOTIFICATIONS}${NOTIF_PUSH}/`, { params });
  return res;
};

export const createPushSubscription = async (data: any) => {
  const res = await apiHelper.post(`${NOTIFICATIONS}/subscribe`, data);
  return res;
};

export const unsubscribePush = async (data: any) => {
  const res = await apiHelper.post(
    `${NOTIFICATIONS}${NOTIF_UNSUBSCRIBE}/`,
    data
  );
  return res;
};



