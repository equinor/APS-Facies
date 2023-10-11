<template>
  <v-select v-model="conformity" :items="options" :dark="dark" variant="underlined"/>
</template>

<script setup lang="ts">
import { Zone } from '@/utils/domain'
import { ZoneConformOption } from '@/utils/domain/zone'
import { ListItem } from '@/utils/typing'
import { computed } from 'vue'
import { useZoneStore } from '@/stores/zones'

type Props = {
  value: Zone
  dark?: boolean
}
const props = withDefaults(defineProps<Props>(), { dark: false })

const zoneStore = useZoneStore()

const conformity = computed({
  get: () => props.value.conformity,
  set: (value: ZoneConformOption) =>
    zoneStore.setConformity(props.value, value),
})

const options: ListItem<string>[] = [
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
