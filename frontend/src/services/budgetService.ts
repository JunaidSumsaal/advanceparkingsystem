import api from "./api";
import { BUDGETS } from './constants';

export const createBudget = async (data: any) => {
  const res = await api.post(`${BUDGETS}`, data);
  return res.data;
};
