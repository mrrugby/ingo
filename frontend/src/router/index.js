import { createRouter, createWebHistory } from "vue-router";

import { dashboardRouteForRole, useAuthStore } from "../stores/auth";
import CaretakerDashboard from "../views/dashboards/CaretakerDashboard.vue";
import LandlordDashboard from "../views/dashboards/LandlordDashboard.vue";
import SuperAdminDashboard from "../views/dashboards/SuperAdminDashboard.vue";
import TenantDashboard from "../views/dashboards/TenantDashboard.vue";
import LoginView from "../views/LoginView.vue";
import NotFoundView from "../views/NotFoundView.vue";
import TenantActivationView from "../views/TenantActivationView.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "login", component: LoginView, meta: { public: true } },
  { path: "/activate", name: "activate", component: TenantActivationView, meta: { public: true } },
  { path: "/dashboard/super-admin", component: SuperAdminDashboard, meta: { roles: ["super_admin"] } },
  { path: "/dashboard/landlord", component: LandlordDashboard, meta: { roles: ["landlord"] } },
  { path: "/dashboard/caretaker", component: CaretakerDashboard, meta: { roles: ["caretaker"] } },
  { path: "/dashboard/tenant", component: TenantDashboard, meta: { roles: ["tenant"] } },
  { path: "/:pathMatch(.*)*", component: NotFoundView, meta: { public: true } }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  await auth.initialize();

  const user = auth.state.user;
  if (to.meta.public) {
    if (to.name === "login" && user) {
      return dashboardRouteForRole(user.role);
    }
    return true;
  }

  if (!user) {
    return "/login";
  }

  const allowedRoles = to.meta.roles || [];
  if (!allowedRoles.includes(user.role)) {
    return dashboardRouteForRole(user.role);
  }

  return true;
});

export default router;

