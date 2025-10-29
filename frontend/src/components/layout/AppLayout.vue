<template>
  <div class="app-layout">
    <AppHeader />
    <div class="app-body">
      <AppTabs v-model="activeTab" @change="handleTabChange">
        <DeviceOverview v-show="activeTab === 'device'" />
        <DataExport v-show="activeTab === 'export'" />
      </AppTabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './AppHeader.vue'
import AppTabs from './AppTabs.vue'
import DeviceOverview from '../../views/DeviceOverview.vue'
import DataExport from '../../views/DataExport.vue'

const activeTab = ref('device')

const handleTabChange = (tab) => {
  activeTab.value = tab
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-background-secondary);
}

.app-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>