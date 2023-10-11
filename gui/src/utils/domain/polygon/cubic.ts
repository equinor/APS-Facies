import { DEFAULT_CUBIC_LEVELS } from '@/config'
import Polygon, {
  PolygonArgs,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import { ID } from '@/utils/domain/types'

export type Level = number[]

interface CubicPolygonArgs extends PolygonArgs {
  // eslint-disable-next-line no-use-before-define
  parent?: CubicPolygon | null
  // eslint-disable-next-line no-use-before-define
  children?: CubicPolygon[]
}

export interface CubicPolygonSpecification extends PolygonSpecification {
  level: Level
}

export interface CubicPolygonSerialization extends PolygonSerialization {
  parent: ID | null
  children: ID[]
}

export default class CubicPolygon extends Polygon {
  public parent: CubicPolygon | null
  public children: CubicPolygon[]

  public constructor({
    parent = null,
    children = [],
    ...rest
  }: CubicPolygonArgs) {
    super(rest)
    this.parent = parent
    if (
      this.parent &&
      this.parent instanceof CubicPolygon &&
      !this.parent.children.map((child): ID => child.id).includes(this.id)
    ) {
      this.parent.children.push(this)
    }
    this.children = children
  }

  public get level(): Level {
    if (this.parent === null) return []
    let level = this.parent.level.concat([this.order])
    if (this.children.length === 0) {
      if (
        /* eslint-disable-next-line yoda */
        0 < DEFAULT_CUBIC_LEVELS &&
        DEFAULT_CUBIC_LEVELS < Number.POSITIVE_INFINITY &&
        level.length < DEFAULT_CUBIC_LEVELS
      ) {
        const fill = Array(DEFAULT_CUBIC_LEVELS - level.length).fill(0)
        level = level.concat(fill)
      }
    }
    return level
  }

  public get atLevel(): number {
    const level: number = this.level.findIndex((level): boolean => level === 0)
    return level >= 0 ? level : this.level.length
  }

  public add(child: CubicPolygon): void {
    child.parent = this
    this.children.push(child)
  }

  public get specification(): CubicPolygonSpecification {
    return {
      ...super.specification,
      id: this.id,
      level: this.level,
    }
  }

  public toJSON(): CubicPolygonSerialization {
    return {
      ...super.toJSON(),
      parent: this.parent ? this.parent.id : null,
      children: this.children.map((child): ID => child.id),
    }
  }
}
