<template>
  <div v-if="isVisible" class="install-banner">
    <div>
      <strong>Install INGO</strong>
      <p>Keep onboarding handy on low-end Android devices with the PWA install.</p>
    </div>
    <button class="button ghost" type="button" @click="installApp">Install</button>
  </div>
</template>

<script setup>
import { ref } from "vue";

const deferredPrompt = ref(null);
const isVisible = ref(false);

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  deferredPrompt.value = event;
  isVisible.value = true;
});

async function installApp() {
  if (!deferredPrompt.value) {
    return;
  }
  deferredPrompt.value.prompt();
  await deferredPrompt.value.userChoice;
  deferredPrompt.value = null;
  isVisible.value = false;
}
</script>

