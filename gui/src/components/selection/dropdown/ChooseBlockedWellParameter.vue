<template>
  <choose-bw-parameter
    parameter-type="blockedWell"
    label="Blocked well parameter"
    warn-message="This will remove all facies, and truncation rules."
  />
</template>

<script setup lang="ts">
import ChooseBwParameter from '@/components/selection/dropdown/BaseBlockedWellParameter.vue'
</script>
