<template>
  <v-select v-model="conformity" :items="options" :dark="dark" variant="underlined"/>
</template>

<script setup lang="ts">
import type { Zone } from '@/utils/domain'
import type { ZoneConformOption } from '@/utils/domain/zone'
import type { ListItem } from '@/utils/typing'
import { computed } from 'vue'
import { useZoneStore } from '@/stores/zones'

const props = withDefaults(defineProps<{
  value: Zone
  dark?: boolean
}>(), {
  dark: false,
})

const zoneStore = useZoneStore()

const conformity = computed({
  get: () => props.value.conformity,
  set: (value: ZoneConformOption) =>
    zoneStore.setConformity(props.value, value),
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
