import api from './api';
import { ANALYTICS, EXPENSES, CHARTS, SUGGESTIONS } from './constants';

export const getAnalyticsOverview = async (month: string) => {
  const res = await api.get(`${ANALYTICS}?month=${month}`);
  return res.data;
};

export const getRecentExpenses = async (page = 1, limit = 10) => {
  const res = await api.get(`${EXPENSES}?page=${page}&limit=${limit}`);
  return res.data;
};

export const getExpenseTrends = async (year: string) => {
  const res = await api.get(`${CHARTS}/trends?year=${year}`);
  return res.data;
};

export const getCategoryBreakdown = async (month: string) => {
  const res = await api.get(`${CHARTS}/breakdown?month=${month}`);
  return res.data;
};

export const getExpenseComparison = async (month: string) => {
  const res = await api.get(`${CHARTS}/comparison?month=${month}`);
  return res.data;
};

export const getComparisonData = async (month: string) => {
  const res = await api.get(`${CHARTS}/comparison?month=${month}`);
  return res.data;
};

export const getTrendsData = async (year: string) => {
  const res = await api.get(`${CHARTS}/trends?year=${year}`);
  return res.data;
};

export const getfetchSuggestions = async (params: { month?: string; page?: number; limit?: number }) => {
  const query = new URLSearchParams();

  if (params.month) query.append('month', params.month);
  if (params.page) query.append('page', params.page.toString());
  if (params.limit) query.append('limit', params.limit.toString());

  const response = await api.get(`${SUGGESTIONS}?${query.toString()}`);
  return response.data;
};

