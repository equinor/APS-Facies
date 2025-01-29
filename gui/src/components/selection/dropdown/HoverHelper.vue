<!--
This component makes it possible to capture is the user is hovering over a disabled item
Vuetify 3's v-hover will not trigger on disabled elements
In our case, we some time want to toggle a tooltip if an element is disabled
-->
<template>
  <div
    @mouseenter="() => (isHovering = true)"
    @mouseleave="() => (isHovering = false)"
  >
    <slot name="default" :is-hovering="isHovering" />
  </div>
</template>

<script setup lang="ts">
import { ref, defineSlots } from 'vue'

const isHovering = ref(false)

defineSlots<{
  'default'(props: { isHovering: boolean }): void
}>()
</script>
