import api from "./api";
import { EXPENSES } from './constants';

export const createExpense = async (data: any) => {
  const res = await api.post(`${EXPENSES}`, data);
  return res.data;
};


export const getExpenses = async (params: { month?: string; page?: number; limit?: number }) => {
  const query = new URLSearchParams();

  if (params.month) query.append('month', params.month);
  if (params.page) query.append('page', params.page.toString());
  if (params.limit) query.append('limit', params.limit.toString());

  const response = await api.get(`${EXPENSES}?${query.toString()}`);
  return response.data;
};

