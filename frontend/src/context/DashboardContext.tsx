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
  getAdminDashboard,
} from "../services/dashboardApi";
import type {
  DashboardContextType,
  DriverDashboard,
  AttendantDashboard,
  ProviderDashboard,
  SpotEvaluationReport,
  AdminDashboard,
} from "../types/context/dashboard";

const DashboardContext = createContext<DashboardContextType | undefined>(
  undefined
);

export const DashboardProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [driver, setDriver] = useState<DriverDashboard | null>(null);
  const [attendant, setAttendant] = useState<AttendantDashboard | null>(null);
  const [provider, setProvider] = useState<ProviderDashboard | null>(null);
  const [spotReports, setSpotReports] = useState<SpotEvaluationReport[]>([]);
  const [admin, setAdmin] = useState<AdminDashboard | null>(null);
  
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch Admin Dashboard
  const fetchAdmin = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getAdminDashboard();
      setAdmin(res);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch admin dashboard");
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch Driver Dashboard
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

  // Fetch Attendant Dashboard
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

  // Fetch Provider Dashboard
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

  // Fetch Spot Evaluation Reports
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
        admin,
        spotReports,
        fetchAdmin,
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

// Custom hook to access Dashboard Context
// eslint-disable-next-line react-refresh/only-export-components
export const useDashboardContext = () => {
  const ctx = useContext(DashboardContext);
  if (!ctx) {
    throw new Error(
      "useDashboardContext must be used within DashboardProvider"
    );
  }
  return ctx;
};
