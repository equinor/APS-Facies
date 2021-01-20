import { Identified } from '@/utils/domain/bases/interfaces'
import { TruncationRuleType } from '@/utils/domain/truncationRule/base'
import { ID } from '@/utils/domain/types'

export interface TruncationRuleTemplateType {
  name: string
  type: TruncationRuleType
  order: number
}

export type TruncationRuleTemplate = TruncationRuleTemplateType & {
  id: ID
}

export interface TruncationRuleTemplateState {
  available: Identified<TruncationRuleTemplate>
}
