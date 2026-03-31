<template>
  <div class="app-root">
    <InstallBanner />
    <RouterView />
  </div>
</template>

<script setup>
import { RouterView } from "vue-router";

import InstallBanner from "./components/InstallBanner.vue";
</script>
