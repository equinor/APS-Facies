<template>
  <base-tooltip :message="active ? message : inactiveMessage">
    <v-icon
      v-if="hasIcon"
      :color="color"
      :icon="__icon"
    />
  </base-tooltip>
</template>

<script setup lang="ts">
import BaseTooltip from '@/components/baseComponents/BaseTooltip.vue'
import type { GlobalFacies } from '@/utils/domain'
import type { ID } from '@/utils/domain/types'
import { computed } from 'vue'
import vuetify from '@/plugins/vuetify'

const props = withDefaults(defineProps<{
  value: GlobalFacies
  icon: string
  current?: ID | null
  active?: boolean
  message?: string
  inactiveMessage?: string
}>(), {
  active: false,
  current: null,
  message: undefined,
  inactiveMessage: undefined,
})

const __icon = computed(() => `$${props.icon}${!props.active ? 'Negated' : ''}`)

const isCurrent = computed(() => props.current === props.value.id)

const color = computed(() => (isCurrent.value ? 'white' : undefined))

const hasIcon = computed<boolean>(() => {
  // Vuetify 3 will throw an error if the icon does not exist, rather than not showing anything as was the case in 2
  const name = __icon.value.replace('$', '')
  const exists = !!vuetify.icons.aliases[name]
  if (!exists) {
    console.warn(`Tried to use icon ${name}, but it does not exist`)
  }
  return exists
})
</script>
