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
import { CustomerProfilePage } from "@/features/customer/pages/CustomerProfilePage";
import { EditProject } from "@/features/customer/pages/EditProject";
import { SpecialistsCatalog } from "@/features/customer/pages/SpecialistsCatalog";

// Public specialist profile
import { SpecialistProfilePublicPage } from "@/features/specialists/pages/SpecialistProfilePublicPage";

// Shared
import { NotificationsPage } from "@/features/notifications/pages/NotificationsPage";
import { NotFoundPage } from "@/features/landing/pages/NotFoundPage";

function RequireAuth({
  role,
  enforceOnboarding = true,
}: {
  role?: "specialist" | "customer";
  enforceOnboarding?: boolean;
}) {
  const { user, accessToken } = useAuthStore();
  if (!accessToken || !user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  if (enforceOnboarding && user.profile_complete === false) {
    if (user.role === "specialist") {
      return <Navigate to="/s/profile?onboarding=1" replace />;
    }
    if (user.role === "customer") {
      return <Navigate to="/c/profile?onboarding=1" replace />;
    }
  }
  return <Outlet />;
}

function AllowGuestOrSpecialist() {
  const { user, accessToken, isGuest } = useAuthStore();
  if (isGuest) return <Outlet />;
  if (!accessToken || !user) return <Navigate to="/login" replace />;
  if (user.role !== "specialist") return <Navigate to="/" replace />;
  if (user.profile_complete === false) {
    return <Navigate to="/s/profile?onboarding=1" replace />;
  }
  return <Outlet />;
}

/**
 * Delayed-auth guard for /c/new: anonymous visitors and authenticated
 * customers can both view the form. Authenticated specialists are
 * redirected away — they don't post projects.
 */
function AllowAnonymousOrCustomer() {
  const { user, accessToken } = useAuthStore();
  if (!accessToken || !user) return <Outlet />; // anonymous OK
  if (user.role === "customer") return <Outlet />;
  return <Navigate to="/s" replace />;
}

export const router = createBrowserRouter([
  {
    element: <Shell />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },

      // Public specialist profile — accessible to everyone (guests, customers,
      // and the specialist themselves).
      { path: "specialists/:id", element: <SpecialistProfilePublicPage /> },

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
          { path: "s/archive", element: <SpecialistArchive /> },
        ],
      },
      {
        // /s/profile is exempt from the onboarding gate so the user can
        // actually fill it in.
        element: <RequireAuth role="specialist" enforceOnboarding={false} />,
        children: [{ path: "s/profile", element: <SpecialistProfilePage /> }],
      },

      {
        element: <AllowAnonymousOrCustomer />,
        children: [{ path: "c/new", element: <CreateProject /> }],
      },
      {
        element: <RequireAuth role="customer" />,
        children: [
          { path: "c", element: <CustomerDashboard /> },
          { path: "c/projects", element: <CustomerProjects /> },
          { path: "c/projects/:id", element: <CustomerProjectDetail /> },
          { path: "c/projects/:id/edit", element: <EditProject /> },
          { path: "c/specialists", element: <SpecialistsCatalog /> },
        ],
      },
      {
        // Exempt from the onboarding gate so the user can actually fill the
        // display name in.
        element: <RequireAuth role="customer" enforceOnboarding={false} />,
        children: [{ path: "c/profile", element: <CustomerProfilePage /> }],
      },

      {
        element: <RequireAuth />,
        children: [{ path: "notifications", element: <NotificationsPage /> }],
      },

      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
