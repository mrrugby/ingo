<template>
  <DashboardShell
    eyebrow="Tenant"
    title="Your tenant profile"
    subtitle="Your phone number is now locked. Contact your caretaker for future changes."
  >
    <StatGrid :items="stats" />

    <PanelCard title="Profile">
      <div class="stack">
        <div class="info-row">
          <span>Name</span>
          <strong>{{ profile.name }}</strong>
        </div>
        <div class="info-row">
          <span>Phone number</span>
          <strong>{{ profile.phone_number }}</strong>
        </div>
        <div class="info-row">
          <span>Property</span>
          <strong>{{ profile.property?.name }}</strong>
        </div>
        <div class="info-row">
          <span>Location</span>
          <strong>{{ profile.property?.location }}</strong>
        </div>
      </div>
    </PanelCard>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { apiRequest } from "../../api/client";
import DashboardShell from "../../components/DashboardShell.vue";
import PanelCard from "../../components/PanelCard.vue";
import StatGrid from "../../components/StatGrid.vue";

const dashboard = ref({ profile: { property: {} } });

const profile = computed(() => dashboard.value.profile || { property: {} });
const stats = computed(() => [
  { label: "Account", value: "Active" },
  { label: "Property", value: profile.value.property?.name || "Not set" }
]);

async function loadDashboard() {
  dashboard.value = await apiRequest("/auth/dashboard/");
}

onMounted(loadDashboard);
</script>

