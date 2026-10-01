<template>
  <labeled-field label="Facies Realization parameter">
    <template #default="{ fieldAttrs }">
      <v-combobox
        v-bind="fieldAttrs"
        v-model="faciesRealizationParameter"
        :items="available"
        :disabled="disabled"
        :messages="disabled ? disabledMessage : undefined"
      />
    </template>
  </labeled-field>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import LabeledField from '@/components/baseComponents/LabeledField.vue'
import { useParameterRealizationStore } from '@/stores/parameters/realization'

type Props = {
  disabled?: boolean
  disabledMessage?: string
}
withDefaults(defineProps<Props>(), {
  disabled: false,
  disabledMessage: '',
})

const parameterRealizationStore = useParameterRealizationStore()

const faciesRealizationParameter = computed({
  get: () => parameterRealizationStore.selected,
  set: (value: string | null) => (parameterRealizationStore.selected = value),
})

const available = computed(() => parameterRealizationStore.available)
</script>
