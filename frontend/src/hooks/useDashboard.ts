import { useDashboardContext } from '../context/DashboardContext';

export const useDashboard = () => {
  const {
    driver,
    attendant,
    provider,
    spotReports,
    fetchDriver,
    fetchAttendant,
    fetchProvider,
    fetchSpotReports,
    loading,
    error,
    setError,
    setLoading,
  } = useDashboardContext();

  return {
    driver,
    attendant,
    provider,
    spotReports,
    fetchDriver,
    fetchAttendant,
    fetchProvider,
    fetchSpotReports,
    loading,
    error,
    setError,
    setLoading,
  };
};
