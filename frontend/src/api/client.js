const STORAGE_KEY = "ingo-auth";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

let refreshPromise = null;

export class ApiError extends Error {
  constructor(status, payload) {
    super(extractErrorMessage(payload) || `Request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

function extractErrorMessage(payload) {
  if (!payload) {
    return "";
  }

  if (typeof payload === "string") {
    return payload;
  }

  if (payload.detail && typeof payload.detail === "string") {
    return payload.detail;
  }

  const firstValue = Object.values(payload)[0];
  if (Array.isArray(firstValue) && firstValue.length) {
    return String(firstValue[0]);
  }

  if (typeof firstValue === "string") {
    return firstValue;
  }

  return "";
}

export function getStoredAuth() {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return { access: "", refresh: "" };
  }

  try {
    const parsed = JSON.parse(raw);
    return { access: parsed.access || "", refresh: parsed.refresh || "" };
  } catch {
    return { access: "", refresh: "" };
  }
}

export function setStoredAuth(access, refresh) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ access, refresh }));
}

export function clearStoredAuth() {
  window.localStorage.removeItem(STORAGE_KEY);
}

async function parseResponse(response) {
  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
}

async function refreshAccessToken() {
  const stored = getStoredAuth();
  if (!stored.refresh) {
    return false;
  }

  if (!refreshPromise) {
    refreshPromise = fetch(`${API_BASE_URL}/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: stored.refresh })
    })
      .then(async (response) => {
        if (!response.ok) {
          clearStoredAuth();
          return false;
        }

        const payload = await response.json();
        setStoredAuth(payload.access, stored.refresh);
        return true;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
}

export async function apiRequest(path, options = {}) {
  const {
    method = "GET",
    body,
    headers = {},
    requireAuth = true,
    retryOnUnauthorized = true
  } = options;

  const stored = getStoredAuth();
  const mergedHeaders = { ...headers };

  if (body !== undefined) {
    mergedHeaders["Content-Type"] = "application/json";
  }

  if (requireAuth && stored.access) {
    mergedHeaders.Authorization = `Bearer ${stored.access}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: mergedHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined
  });

  if (response.status === 401 && requireAuth && retryOnUnauthorized) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return apiRequest(path, { ...options, retryOnUnauthorized: false });
    }
  }

  const payload = await parseResponse(response);
  if (!response.ok) {
    throw new ApiError(response.status, payload);
  }

  return payload;
}

