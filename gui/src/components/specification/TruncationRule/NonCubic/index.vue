<template>
  <truncation-rule-specification :value="value" :table="PolygonTable" />
</template>

<script setup lang="ts">
import type { NonCubic } from '@/utils/domain'
import TruncationRuleSpecification from '@/components/specification/TruncationRule/main.vue'
import PolygonTable from './table.vue'

defineProps<{ value: NonCubic }>()
</script>
