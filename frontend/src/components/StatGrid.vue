<template>
  <div class="stat-grid">
    <article v-for="item in items" :key="item.label" class="stat-card">
      <span>{{ item.label }}</span>
      <strong>{{ item.value }}</strong>
    </article>
  </div>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
});
</script>
