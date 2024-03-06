import type { InstantiatedTruncationRule } from '@/utils/domain'
import type { AvailableOptionSerialization } from '@/stores/parameters/serialization/helpers'
import type { TruncationRuleSerialization, TruncationRuleType } from '@/utils/domain/truncationRule/base'
import type { ID } from '@/utils/domain/types'
import { useTruncationRuleStore } from '@/stores/truncation-rules/index'
import { useTruncationRulePresetStore } from '@/stores/truncation-rules/presets'
import type { BayfillPolygonSerialization } from '@/utils/domain/polygon/bayfill'
import type { NonCubicPolygonSerialization } from '@/utils/domain/polygon/nonCubic'
import type { CubicPolygonSerialization } from '@/utils/domain/polygon/cubic'
import type { OverlayPolygonSerialization } from '@/utils/domain/polygon/overlay'

export type TruncationRuleStoreSerialization = AvailableOptionSerialization<TruncationRuleSerialization<
  | BayfillPolygonSerialization
  | NonCubicPolygonSerialization
  | CubicPolygonSerialization
  | OverlayPolygonSerialization
>> & {
  // A truncation rule serialization can contain different types of truncation rules, and cannot be generic
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
