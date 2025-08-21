import apiHelper from '../utils/apiHelper';
import { DASH_DRIVER, DASH_ATTENDANT, DASH_PROVIDER, DASH_SPOT_EVAL } from './constants';

// Driver Dashboard
export const getDriverDashboard = async () => {
  const res = await apiHelper.get(DASH_DRIVER);
  return res;
};

// Attendant Dashboard
export const getAttendantDashboard = async () => {
  const res = await apiHelper.get(DASH_ATTENDANT);
  return res;
};

// Provider Dashboard
export const getProviderDashboard = async () => {
  const res = await apiHelper.get(DASH_PROVIDER);
  return res;
};

// Spot Evaluation Report
export const getSpotEvaluationReport = async () => {
  const res = await apiHelper.get(DASH_SPOT_EVAL);
  return res;
};
