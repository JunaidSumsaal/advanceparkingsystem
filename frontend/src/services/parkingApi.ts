/* eslint-disable @typescript-eslint/no-explicit-any */
import apiHelper from "../utils/apiHelper";
import {
  PARKING,
  PARK_AVAILABILITY_LOGS,
  PARK_BOOK,
  PARK_BOOKINGS,
  PARK_FACILITIES,
  PARK_NEARBY,
  PARK_NAVIGATE,
  PARK_PREDICTIONS,
  PARK_PRICING_LOGS,
  PARK_PRICING_UPDATE,
  PARK_REVIEW,
} from "./constants";

// Spot Availability Logs
export const getSpotAvailabilityLogs = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_AVAILABILITY_LOGS}`, {
    params,
  });
  return res.data;
};

// Book Spot
export const createBooking = async (data: {
  spot: number;
  start_time: string;
  end_time: string;
}) => {
  const res = await apiHelper.post(`${PARKING}${PARK_BOOK}`, data);
  return res.data;
};

// Bookings
export const getBookings = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_BOOKINGS}`, { params });
  return res.data;
};

export const getBooking = async (id: number) => {
  const res = await apiHelper.get(`${PARKING}${PARK_BOOKINGS}/${id}/`);
  return res.data;
};

export const endBooking = async (id: number) => {
  const res = await apiHelper.post(
    `${PARKING}${PARK_BOOKINGS}/${id}/end_booking/`
  );
  return res.data;
};

// Facilities
export const getFacilities = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_FACILITIES}`, { params });
  return res.data;
};

export const getFacility = async (id: number) => {
  const res = await apiHelper.get(`${PARKING}${PARK_FACILITIES}/${id}/`);
  return res.data;
};

export const archiveFacility = async (id: number) => {
  const res = await apiHelper.post(
    `${PARKING}${PARK_FACILITIES}/${id}/archive/`
  );
  return res.data;
};

export const restoreFacility = async (id: number) => {
  const res = await apiHelper.post(
    `${PARKING}${PARK_FACILITIES}/${id}/restore/`
  );
  return res.data;
};

// Nearby & Navigation
export const getNearbySpots = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_NEARBY}`, { params });
  return res.data;
};

export const navigateToSpot = async (spotId: number) => {
  const res = await apiHelper.get(`${PARKING}${PARK_NAVIGATE}/${spotId}/`);
  return res.data;
};

// Spot Predictions
export const getNearbyPredictions = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_PREDICTIONS}`, { params });
  return res.data;
};

// Pricing
export const getSpotPriceLogs = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_PRICING_LOGS}`, { params });
  return res.data;
};

export const updateDynamicPricing = async () => {
  const res = await apiHelper.post(`${PARKING}${PARK_PRICING_UPDATE}`);
  return res.data;
};

// Reviews
export const createSpotReview = async (data: {
  spot: number;
  rating: number;
  comment?: string;
}) => {
  const res = await apiHelper.post(`${PARKING}${PARK_REVIEW}`, data);
  return res.data;
};
