import { useDashboardContext } from '../context/DashboardContext';

export const useDashboard = () => {
  const {
    admin,
    fetchAdmin,
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
    admin,
    fetchAdmin,
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
