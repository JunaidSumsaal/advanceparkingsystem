/* eslint-disable @typescript-eslint/no-explicit-any */

// Driver Dashboard
export interface DriverDashboard {
  active_bookings: number;
  past_bookings: number;
  total_spending: number;
  upcoming_bookings: Array<{
    parking_spot: {
      latitude: string | number;
      longitude: string | number;
    };
    parking_spot__facility__name: string;
    start_time: string;
    end_time: string;
  }>;
  recent_activity: Array<{
    id: number;
    user__email: string;
    parking_spot__facility__name: string;
    start_time: string;
  }>;
  facility_metrics: Array<{
    facility_name: string;
    total_spots: string;
    occupied_spots: string;
    revenue: string;
    occupancy_rate: string;
  }>;
}

// Admin Dashboard
export interface BookingTrend {
  day: string; // e.g. "2025-08-20"
  count: number; // bookings per day
}

export interface FacilityMetric {
  facility: string;
  occupancy: number;
  revenue: number;
}

export interface RecentBooking {
  id: number;
  user__email: string;
  parking_spot__facility__name: string;
  start_time: string;
}

export interface FacilityMetrics {
  facility_name: string;
  total_spots: number;
  occupied_spots: number;
  revenue: number;
  occupancy_rate: number;
}

// Attendant Dashboard
export interface AttendantDashboard {
  recent_bookings: RecentBooking[];
  managed_facilities_count: number;
  facility_metrics: FacilityMetrics[];
  managed_facilities: number;
  active_spots: number;
  occupied_spots: number;
}

export interface AdminDashboard {
  total_users: number;
  total_facilities: number;
  total_spots: number;
  total_bookings: number;
  user_breakdown: { role: string; count: number }[];

  booking_trends: {
    start_time__date: string; // e.g. "2025-08-17"
    bookings_count: number | null;
  }[];

  facility_metrics: {
    facility_name: string;
    total_spots: number;
    occupied_spots: number;
    total_revenue: number;
    occupancy_rate: number;
  }[];

  revenue: {
    total: number;
    by_facility: {
      parking_spot__facility__name: string;
      total: number | null;
    }[];
  };

  recent_activity: {
    bookings: {
      id: number;
      user__email: string;
      parking_spot__facility__name: string;
      start_time: string; // ISO datetime
    }[];
    users: {
      id: number;
      email: string;
      role: string;
      date_joined: string; // ISO datetime
    }[];
  };

  ai_stats: {
    prediction_logs: number;
    availability_logs: number;
  };
}

export interface FacilityMetric {
  facility_name: string;
  total_spots: number;
  occupied_spots: number;
  total_revenue: number;
  occupancy_rate: number;
}

// Provider Dashboard
export interface ProviderDashboard {
  facilities_count: number;
  spots_count: number;
  total_bookings: number;
  avg_price: number;
  booking_trends: Array<{ day: string; bookings_count: number | null }>;
  facility_metrics: FacilityMetric[];
  occupied_spots: number;
  recent_activity: Array<{
    id: number;
    user__email: string;
    parking_spot__facility__name: string;
    facility_name: string;
    start_time: string;
  }>;
}

// Spot Evaluation Reports
export interface SpotEvaluationReport {
  spot: string;
  precision: number;
  recall: number;
  f1: number;
}

// Dashboard Context Type
export interface DashboardContextType {
  admin: AdminDashboard | null;
  driver: DriverDashboard | null;
  attendant: AttendantDashboard | null;
  provider: ProviderDashboard | null;
  spotReports: SpotEvaluationReport[] | null;

  loading: boolean;
  error?: string | null;

  fetchAdmin: () => Promise<void>;
  fetchDriver: () => Promise<void>;
  fetchAttendant: () => Promise<void>;
  fetchProvider: () => Promise<void>;
  fetchSpotReports: () => Promise<void>;

  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
}
