<template>
  <choose-parameter
    :hide-if-disabled="false"
    :parameter-type="parameterType"
    :label="label"
    warn
    :warn-message="warnMessage"
    :warn-even-when-empty="hasFacies"
  />
</template>

<script setup lang="ts">
import ChooseParameter from '@/components/selection/dropdown/ChooseParameter.vue'
import { computed } from 'vue'
import { useStore } from '../../../store'

type Props = {
  parameterType: string
  label: string
  warnMessage: string
}
defineProps<Props>()

const store = useStore()

const hasFacies = computed(() => store.getters.faciesTable.length > 0)
</script>
