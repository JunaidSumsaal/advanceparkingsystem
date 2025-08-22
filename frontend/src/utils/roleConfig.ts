/* eslint-disable @typescript-eslint/no-explicit-any */
export const roleConfig: Record<string, any> = {
  admin: {
    component: () => import("../pages/dashboard/overview"),
    routes: [
      { path: "analytics", component: () => import("../pages/dashboard/bookings") },
      { path: "expenses", component: () => import("../pages/dashboard/maps") },
      { path: "users", component: () => import("../pages/dashboard/users") },
    ],
  },
  provider: {
    component: () => import("../pages/dashboard/overview/provider"),
    routes: [
      { path: "analytics", component: () => import("../pages/dashboard/bookings") },
      { path: "expenses", component: () => import("../pages/dashboard/maps") },
    ],
  },
  driver: {
    component: () => import("../pages/dashboard/overview/driver"),
    routes: [
      { path: "analytics", component: () => import("../pages/dashboard/bookings") },
    ],
  },
  attendant: {
    component: () => import("../pages/dashboard/overview/attendant"),
    routes: [
      { path: "analytics", component: () => import("../pages/dashboard/bookings") },
    ],
  },
};
