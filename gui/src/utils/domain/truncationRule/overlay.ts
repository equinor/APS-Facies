import APSTypeError from '@/utils/domain/errors/type'
import type FaciesGroup from '@/utils/domain/facies/group'
import Facies from '@/utils/domain/facies/local'
import GaussianRandomField from '@/utils/domain/gaussianRandomField'
import type Polygon from '@/utils/domain/polygon/base'
import {
  type PolygonSerialization,
  type PolygonSpecification,
} from '@/utils/domain/polygon/base'
import OverlayPolygon, {
  type CENTER,
  type OverlayPolygonSerialization,
} from '@/utils/domain/polygon/overlay'
import TruncationRule, {
  type TruncationRuleConfiguration,
  type TruncationRuleSerialization,
  type TruncationRuleSpecification,
} from '@/utils/domain/truncationRule/base'
import type { ID } from '@/utils/domain/types'
import { allSet, getId } from '@/utils/helpers'
import type { TruncationRule as BaseTruncationRule } from '@/utils/domain/truncationRule/index'

export type OverlayTruncationRuleArgs<T extends Polygon> =
  TruncationRuleConfiguration<T> & {
    _useOverlay?: boolean
  }

interface OverlayPolygonSpecification extends PolygonSpecification {
  center: CENTER
  field: string
  over: string[]
}

export interface OverlaySpecification<P extends PolygonSpecification>
  extends TruncationRuleSpecification<P> {
  overlay: OverlayPolygonSpecification[] | null
}

export interface OverlaySerialization<P extends PolygonSerialization>
  extends TruncationRuleSerialization<P | OverlayPolygonSerialization> {
  _useOverlay: boolean
}

export default abstract class OverlayTruncationRule<
  T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
> extends TruncationRule<
  T | OverlayPolygon,
  S | OverlayPolygonSerialization,
  P | OverlayPolygonSpecification
> {
  protected _useOverlay: boolean

  protected constructor({
    _useOverlay,
    ...rest
  }: OverlayTruncationRuleArgs<T>) {
    super(rest)
    this._useOverlay = _useOverlay ?? false

    const additionalConstraints: [() => boolean, string][] = [
      [
        (): boolean => allSet(this.overlayPolygons, 'field'),
        'All overlay polygons must have a Gaussian Random Field assigned to it',
      ],
    ]
    this._constraints.push(...additionalConstraints)
  }

  public get useOverlay(): boolean {
    return this._useOverlay
  }
  public set useOverlay(value: boolean) {
    this._useOverlay = value
  }

  public get overlayPolygons(): OverlayPolygon[] {
    if (!this.useOverlay) return []
    const polygons: OverlayPolygon[] = []
    this.polygons.forEach((polygon): void => {
      if (polygon instanceof OverlayPolygon) polygons.push(polygon)
    })
    return polygons
  }

  public get backgroundPolygons(): T[] {
    const polygons: T[] = []
    this.polygons.forEach((polygon): void => {
      if (!(polygon instanceof OverlayPolygon)) polygons.push(polygon)
    })
    return polygons
  }

  public get fields(): GaussianRandomField[] {
    const backgroundFields = super.fields
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

  public get specification(): OverlaySpecification<P> {
    return {
      overlay:
        this.overlayPolygons.length > 0
          ? this.overlayPolygons.map(
              (polygon): OverlayPolygonSpecification => polygon.specification,
            )
          : null,
      polygons: this.backgroundPolygons.map(
        (polygon): P => polygon.specification as P,
      ),
    }
  }

  public isUsedInDifferentOverlayPolygon(
    group: FaciesGroup | ID,
    field: GaussianRandomField,
  ): boolean {
    const fields: GaussianRandomField[] = []
    this.overlayPolygons
      .filter((polygon): boolean => polygon.group.id === getId(group))
      .forEach((polygon): void => {
        if (polygon.field) fields.push(polygon.field)
      })
    return fields.some((item): boolean => item.id === field.id)
  }

  public isUsedInOverlay(item: GaussianRandomField | Facies): boolean {
    if (item instanceof Facies) {
      return this.overlayPolygons
        .map(({ facies }): ID | '' => getId(facies))
        .includes(item.id)
    } else if (item instanceof GaussianRandomField) {
      for (const polygon of this.overlayPolygons) {
        if (polygon.field !== null && polygon.field.id === item.id) {
          return true
        }
      }
      return false
    } else {
      throw new APSTypeError('The given item is of incompatible type')
    }
  }

  protected toJSON(): OverlaySerialization<S> {
    return {
      ...super.toJSON(),
      _useOverlay: this.useOverlay,
    }
  }
}

export function isOverlayTruncationRule<
  T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends BaseTruncationRule<T, S, P>,
>(
  rule: RULE | OverlayTruncationRule<T, S, P>,
): rule is OverlayTruncationRule<T, S, P> {
  return 'overlay' in rule && !!rule.overlay
}
