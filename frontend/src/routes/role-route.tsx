import { Suspense, lazy } from "react";
import { useIsAuthenticated } from "../hooks/useIsAuthenticated";
import { Navigate } from "react-router-dom";
import Dash from "../components/loader/dashboard";

// Lazy load the components
const Overview = lazy(() => import("../pages/dashboard/overview"));
const Provider = lazy(() => import("../pages/dashboard/overview/provider"));
const Driver = lazy(() => import("../pages/dashboard/overview/driver"));
const Attendant = lazy(() => import("../pages/dashboard/overview/attendant"));

const componentMap: Record<string, React.ComponentType> = {
  admin: Overview,
  provider: Provider,
  driver: Driver,
  attendant: Attendant,
};

export const DashboardSwitch = () => {
  const { user, loading } = useIsAuthenticated();

  if (loading) {
    return <Dash />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const userRole = user.role?.toLowerCase();
  const ComponentToRender = componentMap[userRole];

  if (!ComponentToRender) {
    // fallback if role is not mapped
    return (
      <div className="p-8 text-center">
        <h2 className="text-xl font-semibold">Unknown Role</h2>
        <p className="text-gray-500">
          No dashboard available for role: <strong>{user.role}</strong>
        </p>
      </div>
    );
  }

  return (
    <Suspense fallback={<Dash />}>
      <ComponentToRender />
    </Suspense>
  );
};
