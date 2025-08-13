import axios from 'axios';
import { ANALYTICS, CHARTS, EXPENSES } from './constants';

export const getAnalytics = async (month: string) => {
  const res = await axios.get(`${ANALYTICS}?month=${month}`);
  return res.data;
};

export const getExpenseTrends = async (year: string) => {
  const res = await axios.get(`${CHARTS}/trends?year=${year}`);
  return res.data;
};

export const getCategoryBreakdown = async (month: string) => {
  const res = await axios.get(`${CHARTS}/breakdown?month=${month}`);
  return res.data;
};

export const getRecentExpenses = async (page = 1, limit = 5) => {
  const res = await axios.get(`${EXPENSES}?page=${page}&limit=${limit}`);
  return res.data;
};
