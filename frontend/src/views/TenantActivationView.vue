<template>
  <main class="auth-layout">
    <section class="auth-card accent-card">
      <div class="eyebrow">Tenant Activation</div>
      <h1>Activate your account in two short steps.</h1>
      <p>
        Ask your caretaker or landlord for the 6-digit OTP shown in their dashboard, then finish your setup here.
      </p>
    </section>

    <section class="auth-card">
      <div class="stepper">
        <span :class="{ active: step === 1 }">1. Verify OTP</span>
        <span :class="{ active: step === 2 }">2. Set Password</span>
      </div>

      <form v-if="step === 1" class="stack" @submit.prevent="verifyOtp">
        <label class="field">
          <span>Your full name</span>
          <input v-model="verifyForm.name" placeholder="As entered by your caretaker" required />
        </label>

        <label class="field">
          <span>6-digit OTP</span>
          <input v-model="verifyForm.otp" maxlength="6" placeholder="123456" required />
        </label>

        <p v-if="error" class="message error">{{ error }}</p>
        <button class="button primary" type="submit" :disabled="submitting">
          {{ submitting ? "Checking..." : "Verify and Continue" }}
        </button>
      </form>

      <form v-else class="stack" @submit.prevent="completeActivation">
        <div class="message success">
          OTP verified for <strong>{{ tenantPreview.name }}</strong>. You can confirm or update your phone number now.
        </div>

        <label class="field">
          <span>Phone number</span>
          <input v-model="setupForm.phone_number" placeholder="+254700000000" />
        </label>

        <label class="field">
          <span>Create password</span>
          <input v-model="setupForm.password" type="password" minlength="8" required />
        </label>

        <p class="hint">Phone changes are only allowed during this activation step.</p>
        <p v-if="error" class="message error">{{ error }}</p>
        <button class="button primary" type="submit" :disabled="submitting">
          {{ submitting ? "Finishing..." : "Activate and Open Dashboard" }}
        </button>
      </form>

      <RouterLink class="inline-link" to="/login">Back to login</RouterLink>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";

import { apiRequest } from "../api/client";
import { dashboardRouteForRole, useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

const step = ref(1);
const submitting = ref(false);
const error = ref("");
const activationToken = ref("");
const tenantPreview = reactive({
  name: "",
  phone_number: ""
});

const verifyForm = reactive({
  name: "",
  otp: ""
});

const setupForm = reactive({
  phone_number: "",
  password: ""
});

async function verifyOtp() {
  submitting.value = true;
  error.value = "";

  try {
    const payload = await apiRequest("/tenants/activation/verify/", {
      method: "POST",
      body: verifyForm,
      requireAuth: false
    });
    activationToken.value = payload.activation_token;
    tenantPreview.name = payload.tenant.name;
    tenantPreview.phone_number = payload.tenant.phone_number || "";
    setupForm.phone_number = payload.tenant.phone_number || "";
    step.value = 2;
  } catch (err) {
    error.value = err.message || "Could not verify OTP.";
  } finally {
    submitting.value = false;
  }
}

async function completeActivation() {
  submitting.value = true;
  error.value = "";

  try {
    const result = await auth.finishActivation({
      activation_token: activationToken.value,
      password: setupForm.password,
      ...(setupForm.phone_number ? { phone_number: setupForm.phone_number } : {})
    });
    router.push(dashboardRouteForRole(result.user.role));
  } catch (err) {
    error.value = err.message || "Unable to finish activation.";
  } finally {
    submitting.value = false;
  }
}
</script>

