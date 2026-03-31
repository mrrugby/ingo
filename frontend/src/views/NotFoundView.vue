<template>
  <main class="center-shell">
    <section class="auth-card">
      <h1>Page not found</h1>
      <p>The page you requested does not exist in this MVP.</p>
      <RouterLink class="button primary" to="/login">Return to login</RouterLink>
    </section>
  </main>
</template>

<script setup>
import { RouterLink } from "vue-router";
</script>

