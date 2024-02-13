import type { InstantiatedTruncationRule } from '@/utils/domain'
import type { AvailableOptionSerialization } from '@/stores/parameters/serialization/helpers'
import type { TruncationRuleSerialization, TruncationRuleType } from '@/utils/domain/truncationRule/base'
import type { ID } from '@/utils/domain/types'
import { useTruncationRuleStore } from '@/stores/truncation-rules/index'
import { useTruncationRulePresetStore } from '@/stores/truncation-rules/presets'

export type TruncationRuleStoreSerialization = AvailableOptionSerialization<TruncationRuleSerialization> & {
    preset: {
        template: ID | null
        type: TruncationRuleType | null
    }
}

export function useTruncationRuleStoreSerialization(): TruncationRuleStoreSerialization {
    const { available } = useTruncationRuleStore()
    const { templateId, type } = useTruncationRulePresetStore()
    return {
        available: available.map(rule => (rule as InstantiatedTruncationRule).toJSON()),
        preset: {
            template: templateId,
            type,
        }
    }
}
