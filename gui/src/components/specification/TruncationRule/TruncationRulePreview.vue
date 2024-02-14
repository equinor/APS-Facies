<template>
  <v-list-item>
    <template #title>
      <v-list-item-title v-if="isDevelop || !imageUrl">
        {{ value }}
      </v-list-item-title>
    </template>
    <v-list-item-media>
      <div
        class="tr-preview"
        :style="style"
      >
        <v-row>
          <v-col>
            <v-row>
              <v-img
                v-if="imageUrl"
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
      </div>
    </v-list-item-media>
  </v-list-item>
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
