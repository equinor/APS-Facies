import NonCubicPolygon, {
  NonCubicPolygonSerialization,
  NonCubicPolygonSpecification,
} from '@/utils/domain/polygon/nonCubic'
import OverlayTruncationRule, {
  OverlaySpecification,
  OverlayTruncationRuleArgs
} from '@/utils/domain/truncationRule/overlay'

export type NonCubicSpecification = OverlaySpecification<NonCubicPolygonSpecification>

export default class NonCubic extends OverlayTruncationRule<NonCubicPolygon, NonCubicPolygonSerialization, NonCubicPolygonSpecification> {
  public constructor (props: OverlayTruncationRuleArgs<NonCubicPolygon>) {
    super(props)
  }

  public get type (): 'non-cubic' {
    return 'non-cubic'
  }
}
