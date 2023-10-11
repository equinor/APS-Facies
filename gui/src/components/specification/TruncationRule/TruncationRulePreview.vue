<template>
  <v-row
    class="pt-1 pb-1 pr-0 pl-0 ma-0"
    justify="center"
    align="center"
    no-gutters
  >
    <v-col v-if="isDevelop" cols="12">
      {{ value }}
    </v-col>
    <v-col
      cols="12"
    >
      <v-row
        justify="center"
        align="center"
      >
    <v-col cols="12">
      <v-row v-if="imageUrl" justify="center" align="center">
        <v-img
          aspect-ratio="1"
          eager
          :style="style"
          :alt="altText"
          :src="imageUrl"
          :max-height="DEFAULT_TRUNCATION_RULE_TEMPLATE_PREVIEW_SIZE.height"
          :max-width="DEFAULT_TRUNCATION_RULE_TEMPLATE_PREVIEW_SIZE.width"
        />
      </v-row>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { getDisabledOpacity, isDevelopmentBuild } from '@/utils/helpers/simple'
import { DEFAULT_TRUNCATION_RULE_TEMPLATE_PREVIEW_SIZE } from '@/config'
import { computed } from 'vue'
import {
  type TruncationRuleType,
  truncationRuleTypeNames,
} from '@/utils/domain/truncationRule/base'
type Props = {
  value: string
  type: TruncationRuleType
  altText?: string
  disabled?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  altText: '',
  disabled: false,
})

const imageUrl = computed(
  () => `${window.location.origin}/public/truncation-rules/` +
    `${truncationRuleTypeNames[props.type]}/${props.value}.svg`,
)

const isDevelop = computed(() => isDevelopmentBuild())

const style = computed(() => ({ opacity: getDisabledOpacity(props.disabled) }))
</script>
