import { computed, reactive, readonly } from "vue";

import { apiRequest, clearStoredAuth, getStoredAuth, setStoredAuth } from "../api/client";

const state = reactive({
  access: getStoredAuth().access,
  refresh: getStoredAuth().refresh,
  user: null,
  initialized: false
});

function applySession(payload) {
  setStoredAuth(payload.access, payload.refresh);
  state.access = payload.access;
  state.refresh = payload.refresh;
  state.user = payload.user;
}

function clearSession() {
  clearStoredAuth();
  state.access = "";
  state.refresh = "";
  state.user = null;
}

async function initialize() {
  if (state.initialized) {
    return;
  }

  if (!state.access && !state.refresh) {
    state.initialized = true;
    return;
  }

  try {
    state.user = await apiRequest("/auth/me/");
  } catch {
    clearSession();
  } finally {
    state.initialized = true;
  }
}

async function login(credentials) {
  const payload = await apiRequest("/auth/login/", {
    method: "POST",
    body: credentials,
    requireAuth: false
  });
  applySession(payload);
  return payload.user;
}

async function finishActivation(payload) {
  const result = await apiRequest("/tenants/activation/complete/", {
    method: "POST",
    body: payload,
    requireAuth: false
  });
  applySession(result);
  return result;
}

function logout() {
  clearSession();
}

export function dashboardRouteForRole(role) {
  return {
    super_admin: "/dashboard/super-admin",
    landlord: "/dashboard/landlord",
    caretaker: "/dashboard/caretaker",
    tenant: "/dashboard/tenant"
  }[role] || "/login";
}

export function useAuthStore() {
  return {
    state: readonly(state),
    isAuthenticated: computed(() => Boolean(state.access && state.user)),
    initialize,
    login,
    finishActivation,
    logout
  };
}

