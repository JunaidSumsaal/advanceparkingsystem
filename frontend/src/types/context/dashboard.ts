/* eslint-disable @typescript-eslint/no-explicit-any */
export interface DriverDashboard {
  active_bookings: number;
  past_bookings: number;
}

export interface AttendantDashboard {
  managed_facilities: number;
  active_spots: number;
  occupied_spots: number;
}

export interface ProviderDashboard {
  monthly_bookings(monthly_bookings: any): unknown;
  spot_stats: any;
  facilitiesCount: any;
  spotsCount: any;
  totalBookings: any;
  facilities_count: number;
  spots_count: number;
  total_bookings: number;
  avg_price: number;
  dailyBookings?: { day: string; count: number }[];
  totalSpots?: number;
}

export interface ProviderDashboard {
  facilities_count: number;
  spots_count: number;
  total_bookings: number;
  avg_price: number;
}

export interface SpotEvaluationReport {
  spot: string;
  precision: number;
  recall: number;
  f1: number;
}

export interface DashboardContextType {
  driver: DriverDashboard | null;
  attendant: AttendantDashboard | null;
  provider: ProviderDashboard | null;
  spotReports: SpotEvaluationReport[] | null;
  loading: boolean;
  error?: string | null;
  fetchDriver: () => Promise<void>;
  fetchAttendant: () => Promise<void>;
  fetchProvider: () => Promise<void>;
  fetchSpotReports: () => Promise<void>;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
}


