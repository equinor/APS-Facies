<template>
  <v-row justify="space-between" align="center" no-gutters>
    <v-col cols="0">
      <warning-dialog ref="warning" html />
    </v-col>
    <v-col cols="4">
      <v-checkbox v-model="useRegions" label="Use regions" />
    </v-col>
    <v-col cols="8">
      <choose-parameter
        :disabled="!useRegions"
        regular
        parameter-type="region"
        label="Region parameter"
      />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import ChooseParameter from '@/components/selection/dropdown/ChooseParameter.vue'
import WarningDialog from '@/components/dialogs/JobSettings/WarningDialog.vue'

import { useStore } from '../../../store'
import { computed } from 'vue'

const store = useStore()

const useRegions = computed({
  get: () => store.state.regions.use,
  set: (value: boolean) => store.dispatch('regions/use', { use: value }),
})

// not in use?
const ertMode = computed(() => store.state.fmu.runFmuWorkflows.value)
</script>
