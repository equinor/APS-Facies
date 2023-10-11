<template>
  <div class="color-picker">
    <button
      v-for="color of colors"
      :style="`--bg: ${color}`"
      class="color"
      :class="[value === color ? 'selected' : '']"
      @click="value = color"
      :title="color"
    ></button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Props = {
  modelValue: string
  colors: string[]
}
const props = defineProps<Props>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const value = computed({
  get: () => props.modelValue,
  set: (v: string) => emit('update:modelValue', v),
})
</script>

<style lang="scss">
.color-picker {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  padding: 0.4rem;

  & .color {
    background: var(--bg);
    width: 2.8rem;
    height: 1.4rem;
    cursor: pointer;
    border-radius: 0.5rem;
    box-shadow: inset 0px 0px 0px 2px rgba(0, 0, 0, 0.1);

    &.selected {
      outline: black 3px dashed;
    }
  }
}
</style>
