import { Suspense, lazy } from "react";
import { Navigate } from "react-router-dom";
import Dash from "../components/loader/dashboard";
import { useUserRole } from "../hooks/useUserRole";

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
  const { role, loading } = useUserRole();

  if (loading) {
    return <Dash />;
  }

  if (!role) {
    return <Navigate to="/login" replace />;
  }

  const ComponentToRender = componentMap[role];

  if (!ComponentToRender) {
    // fallback if role is not mapped
    return (
      <div className="p-8 text-center">
        <h2 className="text-xl font-semibold">Unknown Role</h2>
        <p className="text-gray-500">
          No dashboard available for role: <strong>{role}</strong>
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
