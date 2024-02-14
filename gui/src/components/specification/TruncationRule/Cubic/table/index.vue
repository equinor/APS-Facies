<template>
  <v-row justify="center" align="center" no-gutters>
    <v-col cols="12">
      <cubic-truncation-rule-specification :value="value" />
    </v-col>
    <v-col cols="12">
      <cubic-facies-selection v-if="value.root" :value="value" />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import CubicTruncationRuleSpecification from '@/components/specification/TruncationRule/Cubic/table/specification/index.vue'
import CubicFaciesSelection from '@/components/specification/TruncationRule/Cubic/table/table.vue'
import type { Cubic } from '@/utils/domain'

defineProps<{ value: Cubic }>()
</script>
