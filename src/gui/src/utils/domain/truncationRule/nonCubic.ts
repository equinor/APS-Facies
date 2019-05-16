import { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'
import { PolygonSpecification } from '@/utils/domain/polygon/base'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import OverlayTruncationRule, {
  OverlaySpecification,
  OverlayTruncationRuleArgs
} from '@/utils/domain/truncationRule/overlay'
import { getFaciesName } from '@/utils/queries'

interface NonCubicPolygonSpecification extends PolygonSpecification {
  angle: FmuUpdatable
  updatable: boolean
}

export interface NonCubicSpecification extends OverlaySpecification {
  polygons: NonCubicPolygonSpecification[]
}

export default class NonCubic extends OverlayTruncationRule<NonCubicPolygon> {
  public constructor (props: OverlayTruncationRuleArgs<NonCubicPolygon>) {
    super(props)
  }

  public get type (): string {
    return 'non-cubic'
  }

  public get specification (): NonCubicSpecification {
    return {
      ...super.specification,
      polygons: this.backgroundPolygons
        .map((polygon): NonCubicPolygonSpecification => {
          return {
            angle: polygon.angle,
            facies: getFaciesName(polygon),
            fraction: polygon.fraction,
            order: polygon.order,
            updatable: polygon.angle.updatable,
          }
        }),
    }
  }
}
