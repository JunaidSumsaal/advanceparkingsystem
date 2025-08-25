/* eslint-disable @typescript-eslint/no-explicit-any */
import apiHelper from "../utils/apiHelper";
import {
  PARK_AVAILABILITY_LOGS,
  PARK_BOOKINGS,
  PARK_FACILITIES,
  PARK_SPOTS,
  PARK_NAVIGATE,
  PARK_NEARBY,
  PARK_PREDICTIONS,
  PARK_PRICING_LOGS,
  PARK_PRICING_UPDATE,
  PARK_REVIEW,
  PARKING,
} from "./constants";

// --- Availability Logs ---
export const getSpotAvailabilityLogs = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_AVAILABILITY_LOGS}/`, {
    params,
  });
  return res;
};

// --- Bookings ---
export const getBookings = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_BOOKINGS}/`, { params });
  return res;
};

export const createBooking = async (data: any) => {
  const res = await apiHelper.post(`${PARKING}${PARK_BOOKINGS}/`, data);
  return res;
};

export const endBooking = async (id: number) => {
  const res = await apiHelper.post(
    `${PARKING}${PARK_BOOKINGS}/${id}/end_booking/`
  );
  return res;
};

// --- Facilities ---
export const getFacilities = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_FACILITIES}/`, { params });
  return res;
};

export const archiveFacility = async (ids: number[]) => {
  const res = await apiHelper.post(
    `${PARKING}${PARK_FACILITIES}/archive/`,
    { ids }
  );
  return res;
};

export const restoreFacility = async (ids: number[]) => {
  const res = await apiHelper.post(
    `${PARKING}${PARK_FACILITIES}/restore/`,
    { ids }
  );
  return res;
};

export const bulkArchiveFacilities = async (ids: number[]) => {
  const res = await apiHelper.post(
    `${PARKING}${PARK_FACILITIES}/bulk_archive/`,
    { ids }
  );
  return res;
};

export const bulkRestoreFacilities = async (ids: number[]) => {
  const res = await apiHelper.post(
    `${PARKING}${PARK_FACILITIES}/bulk_restore/`,
    { ids }
  );
  return res;
};

// --- Spots ---
export const getSpots = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_SPOTS}/`, { params });
  return res;
};

export const createSpot = async (data: any) => {
  const res = await apiHelper.post(`${PARKING}${PARK_SPOTS}/`, data);
  return res;
};

export const updateSpot = async (id: number, data: any) => {
  const res = await apiHelper.put(`${PARKING}${PARK_SPOTS}/${id}/`, data);
  return res;
};

export const deleteSpot = async (id: number) => {
  const res = await apiHelper.delete(`${PARKING}${PARK_SPOTS}/${id}/`);
  return res;
};

// --- Navigation / Nearby ---
// export const getNearbySpots = async (params?: any) => {
//   const res = await apiHelper.get(`${PARKING}${PARK_NEARBY}/`, { params });
//   return res.data;
// };
export const getNearbySpots = async ({
  lat,
  lng,
  radius = 2,
  limit = 20,
  offset = 0,
}) => {
  const res = await apiHelper.get(`${PARKING}${PARK_NEARBY}/`, {
    params: { lat, lng, radius, limit, offset },
  });
  return res; // { message, total_available, within_radius, results }
};
export const navigateToSpot = async (spotId: number) => {
  const res = await apiHelper.get(`${PARKING}${PARK_NAVIGATE}/${spotId}/`);
  return res;
};

export const getNearbyPredictions = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_PREDICTIONS}/`, { params });
  return res;
};

// --- Pricing & Reviews ---
export const updateDynamicPricing = async () => {
  const res = await apiHelper.post(`${PARKING}${PARK_PRICING_UPDATE}/`);
  return res;
};

export const getSpotPriceLogs = async (params?: any) => {
  const res = await apiHelper.get(`${PARKING}${PARK_PRICING_LOGS}/`, { params });
  return res;
};

export const createSpotReview = async (data: any) => {
  const res = await apiHelper.post(`${PARKING}${PARK_REVIEW}/`, data);
  return res;
};
