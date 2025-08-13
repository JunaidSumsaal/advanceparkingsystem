import { Suspense, lazy } from "react";
import { createBrowserRouter } from "react-router-dom";
import { Error404 } from "@components/404";
import { ProtectedRoute } from "./protected-route";
import { Loading } from "@components/loader";

const LandingPage = lazy(() => import("@pages/landingpage/landingpage"));
const Login = lazy(() => import("@pages/auth/login"));
const Register = lazy(() => import("@pages/auth/register"));
const RestEmail = lazy(() => import("@pages/auth/reset-email"));
const ResetPassword = lazy(() => import("@pages/auth/reset-password"));
const VerifyEmail = lazy(() => import("@pages/auth/verify-email"));
const Dashboard = lazy(() => import("@pages/dashboard/Layout"));
const Overview = lazy(() => import("@pages/dashboard/overview"));
const Analytics = lazy(() => import("@pages/dashboard/analytics"));
const Expenses = lazy(() => import("@pages/dashboard/expenses"));
const Settings = lazy(() => import("@pages/dashboard/settings"));
const Users = lazy(() => import("@pages/dashboard/users"));

export const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <Suspense fallback={<Loading />}>
        <LandingPage />
      </Suspense>
    ),
    errorElement: <Error404 />,
  },
  {
    path: "login",
    element: (
      <Suspense fallback={<Loading />}>
        <Login />
      </Suspense>
    ),
    errorElement: <Error404 />,
  },
  {
    path: "register",
    element: (
      <Suspense fallback={<Loading />}>
        <Register />
      </Suspense>
    ),
  },
  {
    path: "reset-email",
    element: (
      <Suspense fallback={<Loading />}>
        <RestEmail />
      </Suspense>
    ),
  },
  {
    path: "reset-password",
    element: (
      <Suspense fallback={<Loading />}>
        <ResetPassword />
      </Suspense>
    ),
  },
  {
    path: "verify-email",
    element: (
      <Suspense fallback={<Loading />}>
        <VerifyEmail />
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
        <Suspense fallback={<Loading />}>
          <Dashboard />
        </Suspense>
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<Loading />}>
            <Overview />
          </Suspense>
        ),
      },
      {
        path: "analytics",
        element: (
          <Suspense fallback={<Loading />}>
            <Analytics />
          </Suspense>
        ),
      },
      {
        path: "expenses",
        element: (
          <Suspense fallback={<Loading />}>
            <Expenses />
          </Suspense>
        ),
      },
      {
        path: "settings",
        element: (
          <Suspense fallback={<Loading />}>
            <Settings />
          </Suspense>
        ),
      },
      {
        path: "users",
        element: (
          <Suspense fallback={<Loading />}>
            <Users />
          </Suspense>
        ),
      },
    ],
  },
]);
