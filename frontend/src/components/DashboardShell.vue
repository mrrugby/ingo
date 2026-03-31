<template>
  <div class="dashboard-shell">
    <header class="hero-card">
      <div class="eyebrow">{{ eyebrow }}</div>
      <div class="hero-row">
        <div>
          <h1>{{ title }}</h1>
          <p>{{ subtitle }}</p>
        </div>
        <button class="button ghost" type="button" @click="handleLogout">Log Out</button>
      </div>
    </header>

    <slot />
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

defineProps({
  eyebrow: { type: String, default: "INGO" },
  title: { type: String, required: true },
  subtitle: { type: String, required: true }
});

const router = useRouter();
const auth = useAuthStore();

function handleLogout() {
  auth.logout();
  router.push("/login");
}
</script>

