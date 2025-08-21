// Parking types
export interface User {
  id: number;
  username: string;
  role: 'provider' | 'attendant' | 'driver';
}

export interface Facility {
  id: number;
  provider: User;
  name: string;
  capacity: number;
  latitude: number;
  longitude: number;
  address?: string | null;
  attendants: User[];
  created_at: string;
  is_active: boolean;
  is_archived: boolean;
  available_spots: number;
}

export interface Spot {
  id: number;
  facility?: Facility | null;
  name: string;
  latitude: number;
  longitude: number;
  spot_type: 'public' | 'private';
  price_per_hour: number;
  base_price_per_hour: number;
  is_dynamic_pricing: boolean;
  is_available: boolean;
  provider: User;
  created_at: string;
  created_by: User;
  is_active: boolean;
  dynamic_price_per_hour: number;
}

export interface Booking {
  id: number;
  user: User;
  parking_spot: Spot;
  start_time: string;
  end_time?: string | null;
  is_active: boolean;
  total_price?: number | null;
}

export interface SpotReview {
  id: number;
  user: User;
  parking_spot: Spot;
  rating: number; // 1-5
  comment?: string;
  created_at: string;
}

export interface SpotAvailabilityLog {
  id: number;
  parking_spot: Spot;
  timestamp: string;
  is_available: boolean;
  changed_by?: User | null;
}

export interface SpotPredictionLog {
  id: number;
  parking_spot: Spot;
  probability: number;
  predicted_for_time: string;
  model_version: string;
  created_at: string;
}

export interface ModelEvaluationLog {
  id: number;
  auc_score: number;
  brier_score: number;
  tolerance_seconds: number;
  evaluated_at: string;
}

export interface SpotPriceLog {
  id: number;
  parking_spot: Spot;
  old_price: number;
  new_price: number;
  updated_at: string;
}

export interface ArchiveReport {
  id: number;
  user: User;
  title: string;
  body: string;
  period: 'daily' | 'weekly';
  created_at: string;
}

// Parking Context Type
export interface ParkingContextType {
  bookings: Booking[];
  facilities: Facility[];
  nearbySpots: Spot[];

  fetchBookings: () => Promise<void>;
  fetchBooking: (id: number) => Promise<Booking>;
  makeBooking: (data: { spot: number; start_time: string; end_time: string }) => Promise<Booking>;
  endBooking: (id: number) => Promise<Booking>;

  fetchFacilities: () => Promise<void>;
  fetchFacility: (id: number) => Promise<Facility>;

  fetchNearbySpots: () => Promise<void>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  navigateToSpot: (spotId: number) => Promise<any>;
  createSpotReview: (data: { spot: number; rating: number; comment?: string }) => Promise<SpotReview>;

  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  loading: boolean;
  error: string | null;
}
