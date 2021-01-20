import APSTypeError from '@/utils/domain/errors/type'
import FaciesGroup from '@/utils/domain/facies/group'
import Facies from '@/utils/domain/facies/local'
import GaussianRandomField from '@/utils/domain/gaussianRandomField'
import Polygon, { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import OverlayPolygon, { CENTER, OverlayPolygonSerialization } from '@/utils/domain/polygon/overlay'
import TruncationRule, {
  TruncationRuleConfiguration,
  TruncationRuleSerialization,
  TruncationRuleSpecification,
} from '@/utils/domain/truncationRule/base'
import { ID } from '@/utils/domain/types'
import { allSet, getId } from '@/utils/helpers'

export type OverlayTruncationRuleArgs<T extends Polygon = Polygon> = TruncationRuleConfiguration<T> & {
  overlay?: {
    use: boolean
  }
  _useOverlay?: boolean
}

interface OverlayPolygonSpecification extends PolygonSpecification {
  center: CENTER
  field: string
  over: string[]
}

export interface OverlaySpecification<P extends PolygonSpecification = PolygonSpecification> extends TruncationRuleSpecification<P> {
  overlay: OverlayPolygonSpecification[] | null
}

export interface OverlaySerialization<P extends PolygonSerialization = PolygonSerialization> extends TruncationRuleSerialization<P | OverlayPolygonSerialization> {
  _useOverlay: boolean
}

export default abstract class OverlayTruncationRule<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
> extends TruncationRule<
  T | OverlayPolygon,
  S | OverlayPolygonSerialization,
  P | OverlayPolygonSpecification
  > {
  protected _useOverlay: boolean

  protected constructor ({ overlay, _useOverlay, ...rest }: OverlayTruncationRuleArgs<T>) {
    /* TODO: deprecate / combine overlay / _useOverlay */
    super(rest)
    this._useOverlay = typeof _useOverlay === 'undefined'
      ? (overlay ? overlay.use : false)
      : _useOverlay

    const additionalConstraints: ([() => boolean, string])[] = [
      [(): boolean => allSet(this.overlayPolygons, 'field'), 'All overlay polygons must have a Gaussian Random Field assigned to it'],
    ]
    this._constraints.push(...additionalConstraints)
  }

  public get useOverlay (): boolean { return this._useOverlay }

  public get overlayPolygons (): OverlayPolygon[] {
    if (!this.useOverlay) return []
    const polygons: OverlayPolygon[] = []
    this.polygons.forEach((polygon): void => {
      if (polygon instanceof OverlayPolygon) polygons.push(polygon)
    })
    return polygons
  }

  public get backgroundPolygons (): T[] {
    const polygons: T[] = []
    this.polygons.forEach((polygon): void => {
      if (!(polygon instanceof OverlayPolygon)) polygons.push(polygon)
    })
    return polygons
  }

  public get fields (): GaussianRandomField[] {
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

  public get specification (): OverlaySpecification<P> {
    return {
      overlay: this.overlayPolygons.length > 0
        ? this.overlayPolygons.map((polygon): OverlayPolygonSpecification => polygon.specification)
        : null,
      polygons: this.backgroundPolygons
        .map((polygon): P => (polygon.specification as P)),
    }
  }

  public isUsedInDifferentOverlayPolygon (group: FaciesGroup | ID, field: GaussianRandomField): boolean {
    const fields: GaussianRandomField[] = []
    this.overlayPolygons
      .filter((polygon): boolean => polygon.group.id === getId(group))
      .forEach((polygon): void => {
        if (polygon.field) fields.push(polygon.field)
      })
    return fields
      .some((item): boolean => item.id === field.id)
  }

  public isUsedInOverlay (item: GaussianRandomField | Facies): boolean {
    if (item instanceof Facies) {
      return this.overlayPolygons
        .map(({ facies }): ID | '' => getId(facies))
        .includes(item.id)
    } else if (item instanceof GaussianRandomField) {
      for (const polygon of this.overlayPolygons) {
        if (
          polygon.field !== null
          && polygon.field.id === item.id
        ) {
          return true
        }
      }
      return false
    } else {
      throw new APSTypeError('The given item is of incompatible type')
    }
  }

  protected toJSON (): OverlaySerialization<S> {
    return {
      ...super.toJSON(),
      _useOverlay: this.useOverlay,
    }
  }
}
