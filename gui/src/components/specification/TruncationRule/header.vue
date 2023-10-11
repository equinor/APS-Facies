<template>
  <v-row
    no-gutters
    class="truncation-rule-header"
  >
    <v-col>
      <v-select
        ref="chooseTruncationRuleType"
        v-model="type"
        :items="truncationRules"
        label="Rule"
        item-props
        variant="underlined"
      />
    </v-col>
    <v-col>
      <v-combobox
        ref="chooseTruncationRuleTemplate"
        :model-value="preset.template"
        :items="templates"
        :disabled="!type"
        label="Template"
        variant="underlined"
        @update:model-value="(value: string | RuleName) => {
          // value will always be the object from :items
          // ref https://vuetifyjs.com/en/components/combobox/#caveats
          // however, the typing insists that @update:model-value gives a string
          rulePresetStore.change(type, typeof value === 'string' ? value : value.title)
        }"
      >
        <template #item="{ item, props }">
          <truncation-rule-preview
            v-bind="props"
            :value="item.title"
            :type="type!"
            :disabled="item.props.disabled"
            :overlay="item.props.overlay"
          />
        </template>
      </v-combobox>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import TruncationRulePreview from './TruncationRulePreview.vue'

import { computed } from 'vue'
import { type RuleName, useTruncationRuleStore } from '@/stores/truncation-rules'
import { useTruncationRulePresetStore } from '@/stores/truncation-rules/presets'
import type { TruncationRuleType } from '@/utils/domain/truncationRule/base'
import { useOptionStore } from '@/stores/options'

const ruleStore = useTruncationRuleStore()
const rulePresetStore = useTruncationRulePresetStore()
const optionStore = useOptionStore()

const truncationRules = computed(() => ruleStore.ruleTypes)
const templates = computed<RuleName[]>(() => ruleStore.ruleNames
  // templates with overlay will only work as expected if facies selection is automatic
  .filter(template => template.overlay
    ? optionStore.options.automaticFaciesFill
    : true)
)

const preset = computed(() => {
  const rule = ruleStore.current
  return {
    type: rulePresetStore.type,
    template: rulePresetStore.templateId ?? rule?.name ?? '',
  }
})

const type = computed<TruncationRuleType | null>({
  get: () => rulePresetStore.type,
  set: (value: TruncationRuleType | null) =>
    rulePresetStore.change(value, null),
})
</script>
