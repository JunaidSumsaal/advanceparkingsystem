import apiHelper from "../utils/apiHelper";
import { DASHBOARD } from "./constants";

// Driver Dashboard
export const getDriverDashboard = async () => {
  const res = await apiHelper.get(`${DASHBOARD}/driver/`);
  return res;
};

// Attendant Dashboard
export const getAttendantDashboard = async () => {
  const res = await apiHelper.get(`${DASHBOARD}/attendant/`);
  return res;
};

// Provider Dashboard
export const getProviderDashboard = async () => {
  const res = await apiHelper.get(`${DASHBOARD}/provider/`);
  return res;
};

// Spot Evaluation Report
export const getSpotEvaluationReport = async () => {
  const res = await apiHelper.get(`${DASHBOARD}/spot-evaluations/`);
  return res;
};

// Admin Dashboard
export const getAdminDashboard = async () => {
  const res = await apiHelper.get(`${DASHBOARD}/admin/`);
  return res;
};
