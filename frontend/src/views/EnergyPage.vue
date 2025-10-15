<template>
  <div class="energy-page">
    <AppHeader title="能源驾驶舱" />
    <div class="page-body">
      <EnergyCockpit />
    </div>
  </div>
</template>

<script setup>
import AppHeader from '@/components/layout/AppHeader.vue'
import EnergyCockpit from '@/views/EnergyCockpit.vue'
</script>

<style scoped>
.energy-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-background-secondary);
}
.page-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>