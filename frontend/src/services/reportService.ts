import api from './api';
import { REPORTS } from './constants';

export const downloadReport = async (month: string, format: 'pdf' | 'csv') => {
  const response = await api.get(`${REPORTS}/download?month=${month}&format=${format}`, {
    responseType: 'blob',
  });
  return response.data;
};
