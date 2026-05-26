import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/stores/auth";
import { Shell } from "./Shell";

// Public
import { LandingPage } from "@/features/landing/pages/LandingPage";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { RegisterPage } from "@/features/auth/pages/RegisterPage";

// Specialist
import { SpecialistDashboard } from "@/features/specialist/pages/SpecialistDashboard";
import { ProjectFeed } from "@/features/specialist/pages/ProjectFeed";
import { ProjectDetailSpecialist } from "@/features/specialist/pages/ProjectDetailSpecialist";
import { SpecialistProfilePage } from "@/features/specialist/pages/SpecialistProfilePage";
import { SpecialistArchive } from "@/features/specialist/pages/SpecialistArchive";

// Customer
import { CustomerDashboard } from "@/features/customer/pages/CustomerDashboard";
import { CreateProject } from "@/features/customer/pages/CreateProject";
import { CustomerProjects } from "@/features/customer/pages/CustomerProjects";
import { CustomerProjectDetail } from "@/features/customer/pages/CustomerProjectDetail";
import { SpecialistsCatalog } from "@/features/customer/pages/SpecialistsCatalog";

// Shared
import { NotificationsPage } from "@/features/notifications/pages/NotificationsPage";
import { NotFoundPage } from "@/features/landing/pages/NotFoundPage";

function RequireAuth({ role }: { role?: "specialist" | "customer" }) {
  const { user, accessToken } = useAuthStore();
  if (!accessToken || !user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  return <Outlet />;
}

function AllowGuestOrSpecialist() {
  const { user, accessToken, isGuest } = useAuthStore();
  if (isGuest) return <Outlet />;
  if (!accessToken || !user) return <Navigate to="/login" replace />;
  if (user.role !== "specialist") return <Navigate to="/" replace />;
  return <Outlet />;
}

export const router = createBrowserRouter([
  {
    element: <Shell />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },

      {
        element: <AllowGuestOrSpecialist />,
        children: [
          { path: "s/feed", element: <ProjectFeed /> },
          { path: "s/projects/:id", element: <ProjectDetailSpecialist /> },
        ],
      },
      {
        element: <RequireAuth role="specialist" />,
        children: [
          { path: "s", element: <SpecialistDashboard /> },
          { path: "s/profile", element: <SpecialistProfilePage /> },
          { path: "s/archive", element: <SpecialistArchive /> },
        ],
      },

      {
        element: <RequireAuth role="customer" />,
        children: [
          { path: "c", element: <CustomerDashboard /> },
          { path: "c/new", element: <CreateProject /> },
          { path: "c/projects", element: <CustomerProjects /> },
          { path: "c/projects/:id", element: <CustomerProjectDetail /> },
          { path: "c/specialists", element: <SpecialistsCatalog /> },
        ],
      },

      {
        element: <RequireAuth />,
        children: [{ path: "notifications", element: <NotificationsPage /> }],
      },

      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
