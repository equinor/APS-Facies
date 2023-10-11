<template>
  <base-tooltip :message="active ? message : inactiveMessage">
    <v-icon :color="color">
      {{ __icon }}
    </v-icon>
  </base-tooltip>
</template>

<script setup lang="ts">
import BaseTooltip from '@/components/baseComponents/BaseTooltip.vue'
import { GlobalFacies } from '@/utils/domain'
import { ID } from '@/utils/domain/types'
// Doesn't exist in v3?
// import { VuetifyIcon } from "vuetify/types/services/icons";
import { computed } from 'vue'
import vuetify from '@/plugins/vuetify'

type Props = {
  value: GlobalFacies
  icon: string
  current?: ID
  active?: boolean
  message?: string
  inactiveMessage?: string
}
const props = withDefaults(defineProps<Props>(), { active: false })

// TODO: typing
const __icon = computed(() => {
  const icons = vuetify.icons.values
  const iconName = `${props.icon}${!props.active ? 'Negated' : ''}`
  return iconName
  return icons[iconName]
})

const isCurrent = computed(() => props.current === props.value.id)

const color = computed(() => (isCurrent.value ? 'white' : undefined))
</script>
