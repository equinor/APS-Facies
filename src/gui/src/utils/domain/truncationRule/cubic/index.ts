import { DEFAULT_CUBIC_LEVELS } from '@/config'
import CubicPolygon, { CubicPolygonSerialization, CubicPolygonSpecification } from '@/utils/domain/polygon/cubic'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import Direction, { Orientation, OrientationString } from '@/utils/domain/truncationRule/cubic/direction'
import OverlayTruncationRule, {
  OverlaySerialization,
  OverlaySpecification,
  OverlayTruncationRuleArgs
} from '@/utils/domain/truncationRule/overlay'
import { sample } from 'lodash'

type CubicTruncationRuleArgs = OverlayTruncationRuleArgs<CubicPolygon> & {
  direction: Direction | Orientation | OrientationString
}

export interface CubicSpecification extends OverlaySpecification<CubicPolygonSpecification> {
  direction: OrientationString
}

export interface CubicSerialization extends OverlaySerialization<CubicPolygonSerialization> {
  direction: OrientationString
}

export default class Cubic extends OverlayTruncationRule<CubicPolygon, CubicPolygonSerialization, CubicPolygonSpecification> {
  public direction: Direction

  public constructor ({ direction, ...rest }: CubicTruncationRuleArgs) {
    super(rest)
    this.direction = new Direction(direction)
  }

  public get type (): 'cubic' {
    return 'cubic'
  }

  public get root (): CubicPolygon | null {
    let polygon = sample(this.backgroundPolygons)
    if (!polygon) return null
    while (polygon.parent) {
      polygon = polygon.parent
    }
    return polygon
  }

  public get polygons (): (CubicPolygon | OverlayPolygon)[] {
    return super.polygons
      .filter((polygon): boolean => polygon instanceof CubicPolygon ? polygon.children.length === 0 && !!polygon.parent : true)
      .sort((a, b): number => a instanceof CubicPolygon && b instanceof CubicPolygon
        ? a.level.join('').localeCompare(b.level.join(''), undefined, { numeric: true })
        : a.order - b.order
      )
  }

  public get levels (): number {
    const levels = this.backgroundPolygons
      .reduce((levels, polygon): number => polygon.atLevel > levels ? polygon.atLevel : levels, 0)
    return Math.min(DEFAULT_CUBIC_LEVELS, levels)
  }

  public get specification (): CubicSpecification {
    return {
      ...super.specification,
      direction: this.direction.specification,
    }
  }

  public toJSON (): CubicSerialization {
    return {
      ...super.toJSON(),
      direction: this.direction.toString(),
    }
  }
}

export {
  Direction,
  Orientation,
}