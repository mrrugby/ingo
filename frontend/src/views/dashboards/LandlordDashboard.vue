<template>
  <DashboardShell
    eyebrow="Landlord"
    title="Properties, caretakers, and tenant flow"
    subtitle="Set up properties, create caretaker accounts, and monitor onboarding from one place."
  >
    <StatGrid :items="stats" />

    <div class="dashboard-grid">
      <PanelCard title="Create Caretaker">
        <form class="stack" @submit.prevent="createCaretaker">
          <label class="field">
            <span>Full name</span>
            <input v-model="caretakerForm.full_name" required />
          </label>
          <label class="field">
            <span>Email</span>
            <input v-model="caretakerForm.email" type="email" required />
          </label>
          <label class="field">
            <span>Password</span>
            <input v-model="caretakerForm.password" type="password" minlength="8" required />
          </label>
          <button class="button primary" type="submit">Create caretaker</button>
        </form>
      </PanelCard>

      <PanelCard title="Create Property">
        <form class="stack" @submit.prevent="createProperty">
          <label class="field">
            <span>Property name</span>
            <input v-model="propertyForm.name" required />
          </label>
          <label class="field">
            <span>Location</span>
            <input v-model="propertyForm.location" required />
          </label>
          <label class="field">
            <span>Description</span>
            <textarea v-model="propertyForm.description" rows="3" />
          </label>
          <button class="button primary" type="submit">Add property</button>
        </form>
      </PanelCard>

      <PanelCard title="Assign Caretaker">
        <form class="stack" @submit.prevent="assignCaretaker">
          <label class="field">
            <span>Property</span>
            <select v-model="assignmentForm.propertyId" required>
              <option disabled value="">Select property</option>
              <option v-for="property in properties" :key="property.id" :value="property.id">{{ property.name }}</option>
            </select>
          </label>
          <label class="field">
            <span>Caretaker</span>
            <select v-model="assignmentForm.caretakerId" required>
              <option disabled value="">Select caretaker</option>
              <option v-for="caretaker in caretakers" :key="caretaker.id" :value="caretaker.id">{{ caretaker.full_name }}</option>
            </select>
          </label>
          <button class="button primary" type="submit">Assign caretaker</button>
        </form>
      </PanelCard>

      <PanelCard title="Tenant Overview" description="OTP values stay visible here until the tenant completes activation.">
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
const caretakers = ref([]);
const properties = ref([]);
const tenants = ref([]);
const error = ref("");
const message = ref("");

const caretakerForm = reactive({
  full_name: "",
  email: "",
  password: ""
});

const propertyForm = reactive({
  name: "",
  location: "",
  description: ""
});

const assignmentForm = reactive({
  propertyId: "",
  caretakerId: ""
});

const stats = computed(() => [
  { label: "Properties", value: summary.value.counts.properties || 0 },
  { label: "Caretakers", value: summary.value.counts.caretakers || 0 },
  { label: "Tenants", value: summary.value.counts.tenants || 0 },
  { label: "Pending OTPs", value: summary.value.counts.pending_activations || 0 }
]);

async function loadDashboard() {
  const [dashboard, users, propertyList, tenantList] = await Promise.all([
    apiRequest("/auth/dashboard/"),
    apiRequest("/auth/users/"),
    apiRequest("/properties/"),
    apiRequest("/tenants/")
  ]);

  summary.value = dashboard;
  caretakers.value = users;
  properties.value = propertyList;
  tenants.value = tenantList;
}

async function createCaretaker() {
  error.value = "";
  message.value = "";
  try {
    await apiRequest("/auth/users/", {
      method: "POST",
      body: { ...caretakerForm, role: "caretaker" }
    });
    message.value = "Caretaker created.";
    caretakerForm.full_name = "";
    caretakerForm.email = "";
    caretakerForm.password = "";
    await loadDashboard();
  } catch (err) {
    error.value = err.message || "Could not create caretaker.";
  }
}

async function createProperty() {
  error.value = "";
  message.value = "";
  try {
    await apiRequest("/properties/", {
      method: "POST",
      body: propertyForm
    });
    message.value = "Property created.";
    propertyForm.name = "";
    propertyForm.location = "";
    propertyForm.description = "";
    await loadDashboard();
  } catch (err) {
    error.value = err.message || "Could not create property.";
  }
}

async function assignCaretaker() {
  error.value = "";
  message.value = "";
  try {
    await apiRequest(`/properties/${assignmentForm.propertyId}/assign-caretaker/`, {
      method: "POST",
      body: { caretaker_id: Number(assignmentForm.caretakerId) }
    });
    message.value = "Caretaker assigned.";
    await loadDashboard();
  } catch (err) {
    error.value = err.message || "Could not assign caretaker.";
  }
}

onMounted(loadDashboard);
</script>

