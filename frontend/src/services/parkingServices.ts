/* eslint-disable @typescript-eslint/no-explicit-any */
import apiHelper from "../utils/apiHelper";
import { PARK_AVAILABILITY_LOGS, PARK_BOOK, PARK_BOOKINGS, PARK_FACILITIES, PARK_NAVIGATE, PARK_NEARBY, PARK_PREDICTIONS, PARK_PRICING_LOGS, PARK_PRICING_UPDATE, PARK_REVIEW, PARKING } from "./constants";

export const getSpotAvailabilityLogs = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_AVAILABILITY_LOGS}`, { params });
  return res.data;
};

export const bookSpot = async (data: any) => {
  const res = await apiHelper.post(`${PARKING}${PARK_BOOK}`, data);
  return res.data;
};

export const getBookings = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_BOOKINGS}`, { params });
  return res.data;
};

export const endBooking = async (id: number) => {
  const res = await apiHelper.post(`${PARKING}${PARK_BOOKINGS}/${id}/end_booking/`);
  return res.data;
};

export const getFacilities = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_FACILITIES}`, { params });
  return res.data;
};

export const archiveFacility = async (id: number) => {
  const res = await apiHelper.post(`${PARKING}${PARK_FACILITIES}/${id}/archive/`);
  return res.data;
};

export const restoreFacility = async (id: number) => {
  const res = await apiHelper.post(`${PARKING}${PARK_FACILITIES}/${id}/restore/`);
  return res.data;
};

export const getNearbySpots = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_NEARBY}`, { params });
  return res.data;
};

export const navigateToSpot = async (spotId: number) => {
  const res = await apiHelper.get(`${PARKING}${PARK_NAVIGATE}/${spotId}/`);
  return res.data;
};

export const getNearbyPredictions = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_PREDICTIONS}`, { params });
  return res.data;
};

export const updateDynamicPricing = async () => {
  const res = await apiHelper.post(`${PARKING}${PARK_PRICING_UPDATE}`);
  return res.data;
};

// Spot pricing logs
export const getSpotPriceLogs = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_PRICING_LOGS}`, { params });
  return res.data;
};

export const createSpotReview = async (data: any) => {
  const res = await apiHelper.post(`${PARKING}${PARK_REVIEW}`, data);
  return res.data;
};
