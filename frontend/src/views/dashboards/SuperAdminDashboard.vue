<template>
  <DashboardShell
    eyebrow="Super Admin"
    title="System control center"
    subtitle="Create landlords and monitor how the platform is growing."
  >
    <StatGrid :items="stats" />

    <div class="dashboard-grid">
      <PanelCard title="Create Landlord" description="Only the super admin can create landlord accounts.">
        <form class="stack" @submit.prevent="createLandlord">
          <label class="field">
            <span>Full name</span>
            <input v-model="form.full_name" required />
          </label>
          <label class="field">
            <span>Email</span>
            <input v-model="form.email" type="email" required />
          </label>
          <label class="field">
            <span>Password</span>
            <input v-model="form.password" type="password" minlength="8" required />
          </label>
          <p v-if="message" class="message success">{{ message }}</p>
          <p v-if="error" class="message error">{{ error }}</p>
          <button class="button primary" type="submit">Create landlord</button>
        </form>
      </PanelCard>

      <PanelCard title="Landlords" description="Recently created landlord accounts.">
        <div class="list-stack">
          <article v-for="landlord in landlords" :key="landlord.id" class="list-row">
            <div>
              <strong>{{ landlord.full_name }}</strong>
              <p>{{ landlord.email }}</p>
            </div>
            <span class="pill">Landlord</span>
          </article>
          <p v-if="!landlords.length" class="hint">No landlords created yet.</p>
        </div>
      </PanelCard>
    </div>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { apiRequest } from "../../api/client";
import DashboardShell from "../../components/DashboardShell.vue";
import PanelCard from "../../components/PanelCard.vue";
import StatGrid from "../../components/StatGrid.vue";

const summary = ref({ counts: {} });
const landlords = ref([]);
const error = ref("");
const message = ref("");

const form = reactive({
  full_name: "",
  email: "",
  password: ""
});

const stats = computed(() => [
  { label: "Landlords", value: summary.value.counts.landlords || 0 },
  { label: "Caretakers", value: summary.value.counts.caretakers || 0 },
  { label: "Tenants", value: summary.value.counts.tenants || 0 },
  { label: "Pending OTPs", value: summary.value.counts.pending_activations || 0 }
]);

async function loadDashboard() {
  const [dashboard, users] = await Promise.all([apiRequest("/auth/dashboard/"), apiRequest("/auth/users/")]);
  summary.value = dashboard;
  landlords.value = users;
}

async function createLandlord() {
  error.value = "";
  message.value = "";

  try {
    await apiRequest("/auth/users/", {
      method: "POST",
      body: {
        ...form,
        role: "landlord"
      }
    });
    message.value = "Landlord created successfully.";
    form.full_name = "";
    form.email = "";
    form.password = "";
    await loadDashboard();
  } catch (err) {
    error.value = err.message || "Could not create landlord.";
  }
}

onMounted(loadDashboard);
</script>
