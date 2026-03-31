<template>
  <DashboardShell
    eyebrow="Caretaker"
    title="Tenant onboarding desk"
    subtitle="Create tenants, share OTPs manually, and watch activation progress."
  >
    <StatGrid :items="stats" />

    <div class="dashboard-grid">
      <PanelCard title="Create Tenant">
        <form class="stack" @submit.prevent="createTenant">
          <label class="field">
            <span>Tenant name</span>
            <input v-model="tenantForm.full_name" required />
          </label>
          <label class="field">
            <span>Phone number</span>
            <input v-model="tenantForm.phone_number" required />
          </label>
          <label class="field">
            <span>Property</span>
            <select v-model="tenantForm.property_id" required>
              <option disabled value="">Select property</option>
              <option v-for="property in properties" :key="property.id" :value="property.id">{{ property.name }}</option>
            </select>
          </label>
          <button class="button primary" type="submit">Create tenant + OTP</button>
        </form>
      </PanelCard>

      <PanelCard title="Assigned Properties">
        <div class="list-stack">
          <article v-for="property in properties" :key="property.id" class="list-row">
            <div>
              <strong>{{ property.name }}</strong>
              <p>{{ property.location }}</p>
            </div>
            <span class="pill">{{ property.tenant_count }} tenants</span>
          </article>
          <p v-if="!properties.length" class="hint">No properties assigned yet.</p>
        </div>
      </PanelCard>

      <PanelCard title="Tenant OTP Board" description="Share these codes manually. They disappear once used.">
        <div class="list-stack">
          <article v-for="tenant in tenants" :key="tenant.id" class="tenant-row">
            <div>
              <strong>{{ tenant.full_name }}</strong>
              <p>{{ tenant.property_name }} • {{ tenant.phone_number }}</p>
            </div>
            <div class="otp-block">
              <span class="pill">{{ tenant.is_active ? "Active" : "Pending" }}</span>
              <code v-if="tenant.otp" class="otp-code">{{ tenant.otp }}</code>
            </div>
          </article>
          <p v-if="!tenants.length" class="hint">No tenants added yet.</p>
        </div>
      </PanelCard>
    </div>

    <p v-if="message" class="message success">{{ message }}</p>
    <p v-if="error" class="message error">{{ error }}</p>
  </DashboardShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { apiRequest } from "../../api/client";
import DashboardShell from "../../components/DashboardShell.vue";
import PanelCard from "../../components/PanelCard.vue";
import StatGrid from "../../components/StatGrid.vue";

const summary = ref({ counts: {} });
const properties = ref([]);
const tenants = ref([]);
const error = ref("");
const message = ref("");

const tenantForm = reactive({
  full_name: "",
  phone_number: "",
  property_id: ""
});

const stats = computed(() => [
  { label: "Properties", value: summary.value.counts.properties || 0 },
  { label: "Tenants", value: summary.value.counts.tenants || 0 },
  { label: "Pending OTPs", value: summary.value.counts.pending_activations || 0 }
]);

async function loadDashboard() {
  const [dashboard, propertyList, tenantList] = await Promise.all([
    apiRequest("/auth/dashboard/"),
    apiRequest("/properties/"),
    apiRequest("/tenants/")
  ]);
  summary.value = dashboard;
  properties.value = propertyList;
  tenants.value = tenantList;
}

async function createTenant() {
  error.value = "";
  message.value = "";
  try {
    await apiRequest("/tenants/", {
      method: "POST",
      body: {
        ...tenantForm,
        property_id: Number(tenantForm.property_id)
      }
    });
    message.value = "Tenant created. Share the OTP shown in the list.";
    tenantForm.full_name = "";
    tenantForm.phone_number = "";
    tenantForm.property_id = "";
    await loadDashboard();
  } catch (err) {
    error.value = err.message || "Could not create tenant.";
  }
}

onMounted(loadDashboard);
</script>

