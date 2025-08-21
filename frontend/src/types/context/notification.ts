/* eslint-disable @typescript-eslint/no-explicit-any */
export type NotificationType = 'spot_available' | 'booking_reminder' | 'general';

export interface PushSubscription {
  id: number;
  user: number;
  endpoint: string;
  p256dh: string;
  auth: string;
  created_at: string;
}

export interface Notification {
  id: number;
  user: number;
  title: string;
  body: string;
  type: NotificationType;
  sent_at: string;
  delivered: boolean;
  status: 'pending' | 'sent' | 'failed';
  is_read: boolean;
  read_at?: string | null;
}


export interface EmailPreference {
  id: number;
  user: number;
  receive_emails: boolean;
}

export interface NotificationPreference {
  id: number;
  user: number;
  push_enabled: boolean;
  email_enabled: boolean;
  newsletter_enabled: boolean;
}

export interface NotificationTemplate {
  id: number;
  event_type: NotificationType | 'booking_created' | 'booking_ended';
  title_template: string;
  body_template: string;
  render?: (context: Record<string, any>) => { title: string; body: string };
}

export interface NotificationsContextType {
  notifications: Notification[];
  pushSubscriptions: PushSubscription[];
  emailPreference: EmailPreference | null;
  notificationPreference: NotificationPreference | null;
  templates: NotificationTemplate[];
  unreadCount: number;

  /** Notifications */
  fetchNotifications: () => Promise<void>;
  markRead: (id: number) => Promise<void>;
  markAllRead: () => Promise<void>;
  fetchUnreadCount: () => Promise<void>;

  /** Preferences */
  updateEmailPreference: (receiveEmails: boolean) => Promise<void>;

  /** Push */
  addPushSubscription: (subscription: Omit<PushSubscription, "id" | "created_at">) => Promise<void>;
  removePushSubscription: (subscriptionId: number) => Promise<void>;

  /** Loading / Error */
  loading: boolean;
  error?: string | null;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;

  /** Setters */
  setNotifications: React.Dispatch<React.SetStateAction<Notification[]>>;
  setPushSubscriptions: React.Dispatch<React.SetStateAction<PushSubscription[]>>;
  setEmailPreference: React.Dispatch<React.SetStateAction<EmailPreference | null>>;
  setNotificationPreference: React.Dispatch<React.SetStateAction<NotificationPreference | null>>;
  setTemplates: React.Dispatch<React.SetStateAction<NotificationTemplate[]>>;
}
