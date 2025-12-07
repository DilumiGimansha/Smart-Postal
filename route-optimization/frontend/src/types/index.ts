export interface Address {
  id: number;
  address_line: string;
  city: string;
  postal_code: string;
  latitude: number;
  longitude: number;
}

export interface MailItem {
  id: number;
  tracking_number: string;
  recipient_name: string;
  destination_address: Address;
  priority: 'urgent' | 'regular';
  created_at: string;
  is_delivered: boolean;
}

export interface Coordinate {
  lat: number;
  lng: number;
  index: number;
}

export interface Route {
  id: number;
  route_name: string;
  created_at: string;
  status: 'pending' | 'optimized' | 'in_progress' | 'completed';
  mail_items: MailItem[];
  depot_latitude: number;
  depot_longitude: number;
  total_distance: number | null;
  estimated_time: number | null;
  fuel_saving_percentage: number | null;
  optimized_sequence: number[] | null;
  baseline_sequence: number[] | null;
  optimized_coordinates: Coordinate[] | null;
  baseline_coordinates: Coordinate[] | null;
}

export interface TrainingLog {
  id: number;
  episode: number;
  total_reward: number;
  epsilon: number;
  average_distance: number;
  training_time: string;
}

export interface TrafficData {
  id: number;
  segment_start: string;
  segment_end: string;
  traffic_level: 'low' | 'moderate' | 'heavy' | 'unknown';
  delay_minutes: number;
  timestamp: string;
}

export interface RouteMetrics {
  total_distance: number;
  estimated_time: number;
}

export interface RouteImprovement {
  distance_saved_km: number;
  fuel_saving_percentage: number;
  time_saved_minutes: number;
}

export interface OptimizationResult {
  route: Route;
  optimized_metrics: RouteMetrics;
  baseline_metrics: RouteMetrics;
  improvement: RouteImprovement;
  coordinates: {
    optimized: Coordinate[];
    baseline: Coordinate[];
  };
}