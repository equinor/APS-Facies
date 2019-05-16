import { DEFAULT_CUBIC_LEVELS } from '@/config.json'
import { PolygonSpecification } from '@/utils/domain/polygon/base'
import CubicPolygon, { Level } from '@/utils/domain/polygon/cubic'
import Direction, { Orientation } from '@/utils/domain/truncationRule/cubic/direction'
import OverlayTruncationRule, {
  OverlaySpecification,
  OverlayTruncationRuleArgs
} from '@/utils/domain/truncationRule/overlay'
import { getFaciesName } from '@/utils/queries'
import { sample } from 'lodash'

type CubicTruncationRuleArgs = OverlayTruncationRuleArgs<CubicPolygon> & {
  direction: Direction | Orientation
}

interface CubicPolygonSpecification extends PolygonSpecification {
  level: Level
}

export interface CubicSpecification extends OverlaySpecification {
  direction: string
  polygons: CubicPolygonSpecification[]
}

export default class Cubic extends OverlayTruncationRule<CubicPolygon> {
  public direction: Direction

  public constructor ({ direction, ...rest }: CubicTruncationRuleArgs) {
    super(rest)
    this.direction = new Direction(direction)
  }

  public get type (): string {
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

  public get polygons () {
    return super.polygons
      .filter((polygon): boolean => polygon instanceof CubicPolygon ? polygon.children.length === 0 : true)
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
      polygons: this.backgroundPolygons.map((polygon, index): CubicPolygonSpecification => {
        return {
          id: polygon.id,
          facies: getFaciesName(polygon),
          fraction: polygon.fraction,
          level: polygon.level,
          order: index,
        }
      })
    }
  }

  public toJSON () {
    return {
      ...super.toJSON(),
      polygons: Object.values(this._polygons),
    }
  }
}

export {
  Direction,
  Orientation,
}
