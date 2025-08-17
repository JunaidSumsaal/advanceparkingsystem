import { Suspense, lazy } from "react";
import { createBrowserRouter } from "react-router-dom";
import { Error404 } from "../components/404";
import { ProtectedRoute } from "./protected-route";
import Loader from "../components/loader/loaders";
import LoaderDash from "../components/loader/loaders-dashboard";

const LandingPage = lazy(() => import("../pages/landingpage/landingpage"));
const Login = lazy(() => import("../pages/auth/login"));
const Register = lazy(() => import("../pages/auth/register"));
const Dashboard = lazy(() => import("../pages/dashboard/Layout"));
const Overview = lazy(() => import("../pages/dashboard/overview"));
const Analytics = lazy(() => import("../pages/dashboard/analytics"));
const Expenses = lazy(() => import("../pages/dashboard/expenses"));
const Settings = lazy(() => import("../pages/dashboard/settings"));
const Users = lazy(() => import("../pages/dashboard/users"));

export const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <Suspense fallback={<Loader />}>
        <LandingPage />
      </Suspense>
    ),
    errorElement: <Error404 />,
  },
  {
    path: "login",
    element: (
      <Suspense fallback={<Loader />}>
        <Login />
      </Suspense>
    ),
    errorElement: <Error404 />,
  },
  {
    path: "register",
    element: (
      <Suspense fallback={<Loader />}>
        <Register />
      </Suspense>
    ),
  },
  {
    path: "*",
    element: <Error404 />,
  },
  {
    path: "dashboard",
    element: (
      <ProtectedRoute>
        <Suspense fallback={<LoaderDash />}>
          <Dashboard />
        </Suspense>
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<LoaderDash />}>
            <Overview />
          </Suspense>
        ),
      },
      {
        path: "analytics",
        element: (
          <Suspense fallback={<LoaderDash />}>
            <Analytics />
          </Suspense>
        ),
      },
      {
        path: "expenses",
        element: (
          <Suspense fallback={<LoaderDash />}>
            <Expenses />
          </Suspense>
        ),
      },
      {
        path: "settings",
        element: (
          <Suspense fallback={<LoaderDash />}>
            <Settings />
          </Suspense>
        ),
      },
      {
        path: "users",
        element: (
          <Suspense fallback={<LoaderDash />}>
            <Users />
          </Suspense>
        ),
      },
    ],
  },
]);
