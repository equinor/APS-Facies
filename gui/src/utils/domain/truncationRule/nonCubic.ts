import type NonCubicPolygon from '@/utils/domain/polygon/nonCubic';
import {
  type NonCubicPolygonSerialization,
  type NonCubicPolygonSpecification,
} from '@/utils/domain/polygon/nonCubic'
import OverlayTruncationRule, {
  type OverlaySpecification,
  type OverlayTruncationRuleArgs,
} from '@/utils/domain/truncationRule/overlay'

export type NonCubicSpecification =
  OverlaySpecification<NonCubicPolygonSpecification>

export default class NonCubic extends OverlayTruncationRule<
  NonCubicPolygon,
  NonCubicPolygonSerialization,
  NonCubicPolygonSpecification
> {
  public constructor(props: OverlayTruncationRuleArgs<NonCubicPolygon>) {
    super(props)
  }

  public get type(): 'non-cubic' {
    return 'non-cubic'
  }

  public toJSON () {
    return super.toJSON()
  }
}
