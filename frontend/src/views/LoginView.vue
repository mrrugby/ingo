<template>
  <main class="auth-layout">
    <section class="auth-card accent-card">
      <div class="eyebrow">INGO MVP</div>
      <h1>Structured tenant management for onboarding-first teams.</h1>
      <p>
        Staff sign in with email and password. Tenants activate with OTP, then log in with phone and password.
      </p>
    </section>

    <section class="auth-card">
      <div class="panel-header">
        <div>
          <h2>Sign In</h2>
          <p>Use email if you are staff. Use phone after tenant activation.</p>
        </div>
      </div>

      <form class="stack" @submit.prevent="handleSubmit">
        <label class="field">
          <span>Email or phone number</span>
          <input v-model="form.identifier" placeholder="name@example.com or +254..." required />
        </label>

        <label class="field">
          <span>Password</span>
          <input v-model="form.password" type="password" placeholder="Enter your password" required />
        </label>

        <p v-if="error" class="message error">{{ error }}</p>
        <button class="button primary" type="submit" :disabled="submitting">
          {{ submitting ? "Signing in..." : "Open Dashboard" }}
        </button>
      </form>

      <RouterLink class="inline-link" to="/activate">Activate Tenant Account</RouterLink>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { dashboardRouteForRole, useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

const form = reactive({
  identifier: "",
  password: ""
});

const error = ref("");
const submitting = ref(false);

async function handleSubmit() {
  error.value = "";
  submitting.value = true;

  try {
    const user = await auth.login(form);
    router.push(dashboardRouteForRole(user.role));
  } catch (err) {
    error.value = err.message || "Unable to sign in.";
  } finally {
    submitting.value = false;
  }
}
</script>

