import { GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import APSTypeError from '@/utils/domain/errors/type'
import FaciesGroup from '@/utils/domain/facies/group'
import Facies from '@/utils/domain/facies/local'
import Polygon, { PolygonSpecification } from '@/utils/domain/polygon/base'
import OverlayPolygon, { CENTER } from '@/utils/domain/polygon/overlay'
import TruncationRule, { TruncationRuleConfiguration } from '@/utils/domain/truncationRule/base'
import { ID } from '@/utils/domain/types'
import { getId, allSet } from '@/utils/helpers'

export type OverlayTruncationRuleArgs<T extends Polygon> = TruncationRuleConfiguration<T> & {
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

export interface OverlaySpecification {
  overlay: OverlayPolygonSpecification[] | null
}

export default abstract class OverlayTruncationRule<T extends Polygon> extends TruncationRule<T> {
  protected _useOverlay: boolean

  protected constructor ({ overlay, _useOverlay, ...rest }: OverlayTruncationRuleArgs<T>) {
    /* TODO: deprecate / combine overlay / _useOverlay */
    super(rest)
    this._useOverlay = typeof _useOverlay === 'undefined'
      ? (overlay ? overlay.use : false)
      : _useOverlay

    this._constraints.push(...[
      (): boolean => allSet(this.overlayPolygons, 'field')
    ])
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

  public get specification (): OverlaySpecification {
    return {
      overlay: this.overlayPolygons.length > 0
        ? this.overlayPolygons.map((polygon): OverlayPolygonSpecification => {
          return {
            center: polygon.center,
            facies: polygon.facies ? polygon.facies.name : '',
            field: polygon.field ? polygon.field.name : '',
            fraction: polygon.fraction,
            order: polygon.order,
            over: polygon.group.facies.map((facies): string => facies.name),
          }
        })
        : null,
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
}
