import React, {
  createContext,
  useContext,
  useState,
  useCallback,
} from "react";
import {
  getDriverDashboard,
  getAttendantDashboard,
  getProviderDashboard,
  getSpotEvaluationReport,
} from "../services/dashboardApi";
import type {
  DashboardContextType,
  DriverDashboard,
  AttendantDashboard,
  ProviderDashboard,
  SpotEvaluationReport,
} from "../types/context/dashboard";

const DashboardContext = createContext<DashboardContextType | undefined>(
  undefined
);

export const DashboardProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [driver, setDriver] = useState<DriverDashboard | null>(null);
  const [attendant, setAttendant] = useState<AttendantDashboard | null>(
    null
  );
  const [provider, setProvider] = useState<ProviderDashboard | null>(
    null
  );
  const [spotReports, setSpotReports] = useState<SpotEvaluationReport[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDriver = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getDriverDashboard();
      setDriver(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch driver dashboard");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchAttendant = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getAttendantDashboard();
      setAttendant(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch attendant dashboard");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchProvider = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getProviderDashboard();
      setProvider(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch provider dashboard");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSpotReports = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getSpotEvaluationReport();
      setSpotReports(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch spot evaluation reports");
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <DashboardContext.Provider
      value={{
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
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useDashboardContext = () => {
  const ctx = useContext(DashboardContext);
  if (!ctx)
    throw new Error(
      "useDashboardContext must be used within DashboardProvider"
    );
  return ctx;
};
