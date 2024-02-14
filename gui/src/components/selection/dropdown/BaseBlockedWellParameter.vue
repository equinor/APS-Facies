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
import { useFaciesGlobalStore } from '@/stores/facies/global'
import type { BlockedWellParameterType } from '@/utils/domain/types'

type Props = {
  parameterType: BlockedWellParameterType
  label: string
  warnMessage: string
}
defineProps<Props>()

const faciesGlobalStore = useFaciesGlobalStore()
const hasFacies = computed(() => faciesGlobalStore.available.length > 0)
</script>
