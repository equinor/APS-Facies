<template>
  <v-container class="text-center ma-0 pa-0" fluid>
    <v-row class="xs12 pa-0 ma-0">
      <v-row align="center" justify="center">
        <v-col
          v-for="field in value"
          :key="field.id"
          :ref="`v-flex:${field.id}`"
          class="shrink"
        >
          <h5>{{ field.name }}</h5>
          <gaussian-plot
            v-if="field.simulated"
            pa-0
            ma-0
            :value="field"
            :size="size"
          />
          <v-progress-circular v-else :size="70" indeterminate />
        </v-col>
        <v-col cols="2" align-self="end">
          <color-scale v-if="someSimulated" />
        </v-col>
      </v-row>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import GaussianPlot from './index.vue'
import ColorScale from '@/components/plot/ColorScale.vue'
import { GaussianRandomField } from '@/utils/domain'
import { DEFAULT_SIZE } from '@/config'
import { ref, computed, watch } from 'vue'
import { useStore } from '../../../store'

interface Size {
  max?: {
    width: number
    height: number
  }
  width: number
  height: number
}

const props = defineProps<{ value: GaussianRandomField[] }>()

const store = useStore()

const size = ref<Size>(DEFAULT_SIZE)
const someSimulated = computed(() =>
  props.value.some((field) => field.simulated),
)

watch(props.value, (value: GaussianRandomField[]) => {
  if (store.state.panels.preview.gaussianRandomFields) {
    store.dispatch('gaussianRandomFields/updateSimulations', { fields: value })
  }
})
</script>
