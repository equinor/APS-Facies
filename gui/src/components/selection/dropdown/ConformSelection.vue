<template>
  <labeled-field label="Conformity" position="start">
    <template #default="{ fieldAttrs }">
      <v-select
        v-bind="fieldAttrs"
        v-model="conformity"
        :items="options"
        bg-color="surface"
      />
    </template>
  </labeled-field>
</template>

<script setup lang="ts">
import LabeledField from '@/components/baseComponents/LabeledField.vue'

import type { Zone } from '@/utils/domain'
import type { ZoneConformOption } from '@/utils/domain/zone'
import type { ListItem } from '@/utils/typing'
import { computed } from 'vue'
import { useZoneStore } from '@/stores/zones'

const props = defineProps<{ value: Zone }>()

const zoneStore = useZoneStore()

const conformity = computed({
  get: () => props.value.conformity,
  set: (value: ZoneConformOption) => zoneStore.setConformity(props.value, value),
})

const options: ListItem<ZoneConformOption>[] = [
  {
    value: 'TopConform',
    title: 'Top Conform',
  },
  {
    value: 'BaseConform',
    title: 'Base Conform',
  },
  {
    value: 'Proportional',
    title: 'Proportional',
  },
]
</script>
