import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'
import { useTruncationRuleStore } from '.'
import { notEmpty } from '@/utils'
import type { InstantiatedTruncationRule } from '@/utils/domain'
import type { TruncationRuleType } from '@/utils/domain/truncationRule/base'
import { useTruncationRuleTemplateStore } from '@/stores/truncation-rules/templates'
import { APSError } from '@/utils/domain/errors'

export const useTruncationRulePresetStore = defineStore(
  'truncation-rule-presets',
  () => {
    const type = ref<TruncationRuleType | null>(null)
    const templateId = ref<string | null>(null)

    function fetch(rule: InstantiatedTruncationRule | null = null) {
      const truncationRuleStore = useTruncationRuleStore()
      rule = rule ?? truncationRuleStore.current ?? null
      if (rule) {
        if (rule.type) type.value = rule.type
        if (rule.name) templateId.value = rule.name
      } else {
        $reset()
      }
    }

    function change(
      _type: TruncationRuleType | null,
      _templateId: string | null,
    ) {
      const truncationRuleStore = useTruncationRuleStore()
      const currentRule = truncationRuleStore.current
      if (
        currentRule &&
        (
          _type !== type.value ||
          _templateId !== templateId.value
        )
      ) {
        truncationRuleStore.remove(currentRule)
      }

      if (notEmpty(_type)) {
        type.value = _type
        templateId.value = null
      }

      if (notEmpty(_templateId)) {
        templateId.value = _templateId
        const templateStore = useTruncationRuleTemplateStore()
        if (!templateId.value || !type.value) {
          throw new APSError(
            'templateId and typeId must be set when adding rule from template.',
          )
        }
        templateStore.createRule(templateId.value, type.value)

      }
    }

    function populate(
      _type: TruncationRuleType | null = null,
      _templateId: string | null = null,
    ) {
      if (_type) type.value = _type
      if (_templateId) templateId.value = _templateId
    }

    function $reset() {
      type.value = null
      templateId.value = null
    }

    return {
      type,
      templateId,
      fetch,
      change,
      populate,
      $reset,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useTruncationRulePresetStore, import.meta.hot),
  )
}
