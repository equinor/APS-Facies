<template>
  <truncation-rule-specification :value="value" :table="PolygonTable" />
</template>

<script setup lang="ts">
import TruncationRuleSpecification from '@/components/specification/TruncationRule/main.vue'
import PolygonTable from './table/index.vue'
import type { Cubic } from '@/utils/domain'

defineProps<{ value: Cubic }>()
</script>
