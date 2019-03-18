import { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'
import { GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import { PolygonSpecification } from '@/utils/domain/polygon/base'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import OverlayTruncationRule, {
  OverlaySpecification,
  OverlayTruncationRuleArgs
} from '@/utils/domain/truncationRule/overlay'

type Polygon = NonCubicPolygon | OverlayPolygon

interface NonCubicPolygonSpecification extends PolygonSpecification {
  angle: FmuUpdatable
  updatable: boolean
}

export interface NonCubicSpecification extends OverlaySpecification {
  polygons: NonCubicPolygonSpecification[]
}

export default class NonCubic extends OverlayTruncationRule<Polygon> {
  public constructor (props: OverlayTruncationRuleArgs<Polygon>) {
    super(props)
  }

  public get specification (): NonCubicSpecification {
    return {
      ...super.specification,
      polygons: this.backgroundPolygons
        .map((polygon): NonCubicPolygonSpecification => {
          return {
            angle: polygon.angle,
            facies: polygon.facies ? polygon.facies.name : '',
            fraction: polygon.fraction,
            order: polygon.order,
            updatable: polygon.angle.updatable,
          }
        }),
    }
  }

  public get backgroundFields (): GaussianRandomField[] {
    return this._backgroundFields
  }

  public get backgroundPolygons (): NonCubicPolygon[] {
    const polygons: NonCubicPolygon[] = []
    this.polygons.forEach((polygon): void => {
      if (!(polygon instanceof OverlayPolygon)) polygons.push(polygon)
    })
    return polygons
  }

  public get fields (): GaussianRandomField[] {
    // FIXME
    const backgroundFields = this.backgroundFields
    const overlayFields: GaussianRandomField[] = []
    this.overlayPolygons
      .sort((a, b): number => a.order - b.order)
      .forEach(({ field }): void => {
        if (field && !overlayFields.includes(field)) {
          overlayFields.push(field)
        }
      })
    return [...backgroundFields, ...overlayFields]
  }
}
