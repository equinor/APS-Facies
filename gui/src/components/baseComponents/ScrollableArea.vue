<template>
  <v-responsive class="overflow-y-auto" :height="height" @resize="updateHeight">
    <slot ref="component" />
  </v-responsive>
</template>

<script setup lang="ts">
import { onUnmounted, onMounted, ref } from 'vue'

type Props = {
  offset?: number
}
const props = withDefaults(defineProps<Props>(), {
  // 64 is the height of the toolbar, so not sure why 96 is the magic value.
  offset: 96,
})

const height = ref(0)
const component = ref<HTMLElement | null>(null)

function updateHeight(): void {
  const innerHeight = component.value?.clientHeight ?? window.innerHeight
  height.value = innerHeight - props.offset
}

onMounted(() => {
  updateHeight()
  // Necessary, in order to listen to when RMS' console changes size
  window.addEventListener('resize', updateHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateHeight)
})
</script>
