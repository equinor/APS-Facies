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
        v-model="template"
        :items="templates"
        :disabled="!type"
        label="Template"
        variant="underlined"
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
import { RootGetters } from '@/store/typing'

import TruncationRulePreview from './TruncationRulePreview.vue'

import { isUUID } from '@/utils/helpers'
import { useStore } from '../../../store'
import { computed } from 'vue'

const store = useStore()

const truncationRules = computed(
  () => (store.getters as RootGetters)['truncationRules/ruleTypes'],
)
const templates = computed(
  () => (store.getters as RootGetters)['truncationRules/ruleNames'],
)

const preset = computed(() => {
  const rule = (store.getters as RootGetters).truncationRule
  // TODO:  I think the typing for template here is wrong!
  // Probably should always be a {text: string} object!
  const { type, template } = store.state.truncationRules.preset
  return {
    type: type || (rule ? rule.type : ''),
    template: template ?? rule?.name ?? '',
  }
})

const type = computed<string>({
  get: () => {
    let type: string = preset.value.type
    if (!type) return ''
    if (isUUID(type)) {
      return store.state.truncationRules.templates.types.available[type].name
    }
    const ruleTemplate = Object.values(
      store.state.truncationRules.templates.types.available,
    ).find((item) => item.type === type)

    return ruleTemplate?.name ?? ''
  },
  set: (value: string) =>
    store.dispatch('truncationRules/preset/change', { type: value }),
})

const template = computed({
  get: () => preset.value.template,
  set: (value: string) => {
    store.dispatch('truncationRules/preset/change', { template: value })
  },
})
</script>
