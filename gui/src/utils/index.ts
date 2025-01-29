import { v5 as uuidv5 } from 'uuid'

import type { Named, SimulationSettings } from '@/utils/domain/bases/interfaces'

import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type { TruncationRule } from '@/utils/domain/truncationRule'
import type {
  TruncationRuleSpecification,
  TruncationRuleType,
} from '@/utils/domain/truncationRule/base'
import type { Parent, Polygon } from '@/utils/domain'
import type { ID } from '@/utils/domain/types'

import type { Dependent } from '@/utils/domain/bases/zoneRegionDependent'
import { hasParents } from '@/utils/domain/bases/zoneRegionDependent'

import {
  allSet,
  getId,
  getRandomInt,
  includes,
  isEmpty,
  newSeed,
  notEmpty,
  identify,
} from '@/utils/helpers'
import { useFaciesStore } from '@/stores/facies'
import { useOptionStore } from '@/stores/options'
import { useRootStore } from '@/stores'
import { useZoneStore } from '@/stores/zones'
import { isOverlayTruncationRule } from '@/utils/domain/truncationRule/overlay'
import type { OverlayPolygonSpecification } from '@/utils/domain/polygon/overlay'

function defaultSimulationSettings(): SimulationSettings {
  return {
    gridAzimuth: 0,
    gridSize: { x: 100, y: 100, z: 1 },
    simulationBox: { x: 1000, y: 1000, z: 10 },
    simulationBoxOrigin: { x: 0, y: 0 },
  }
}

function simplify<
  P extends PolygonSpecification | OverlayPolygonSpecification,
  Spec extends TruncationRuleSpecification<P>,
>(specification: Spec, includeOverlay = true): Spec {
  return {
    ...specification,
    polygons: specification.polygons.map((polygon: P): P => {
      return {
        ...polygon,
        facies: polygon.id,
        fraction: 1,
      }
    }),
    overlay:
      'overlay' in specification && includeOverlay
        ? specification.overlay
        : null,
  }
}

interface GlobalFaciesSpecification {
  code: number
  name: string
  probability: number
  inZone: boolean
  inRule: number | boolean
}

interface GaussianRandomFieldSpecification {
  name: string
  inZone: boolean
  inRule: number | boolean
  inBackground: boolean
}

export interface TruncationRuleDescription<P extends PolygonSpecification> {
  type: TruncationRuleType
  globalFaciesTable: GlobalFaciesSpecification[]
  gaussianRandomFields: GaussianRandomFieldSpecification[]
  values: TruncationRuleSpecification<P>
  constantParameters: boolean
}

function makeSimplifiedTruncationRuleSpecification<
  T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends TruncationRule<T, S, P>,
>(rule: RULE): TruncationRuleDescription<P> {
  return {
    type: rule.type,
    globalFaciesTable: (rule.backgroundPolygons as Polygon[]).map(
      (polygon, index): GlobalFaciesSpecification => {
        return {
          code: index,
          name: polygon.id,
          probability: 1 / rule.backgroundPolygons.length,
          inZone: true,
          inRule: true,
        }
      },
    ),
    gaussianRandomFields: ['GRF1', 'GRF2', 'GRF3'].map(
      (field): GaussianRandomFieldSpecification => {
        const included = !(field === 'GRF3' && rule.type !== 'bayfill')
        return {
          name: field,
          inZone: true,
          inRule: included,
          inBackground: included,
        }
      },
    ),
    values: simplify(rule.specification, false),
    constantParameters: true,
  }
}

function makeGlobalFaciesTableSpecification<
  T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends TruncationRule<T, S, P>,
>(rule: RULE): GlobalFaciesSpecification[] {
  const faciesStore = useFaciesStore()
  const optionStore = useOptionStore()

  const facies = faciesStore.selected.filter(
    (facies) =>
      !optionStore.options.filterZeroProbability ||
      (!!facies.previewProbability && facies.previewProbability > 0),
  )
  const cumulativeProbability = facies.reduce(
    (sum, { previewProbability }): number => sum + Number(previewProbability),
    0,
  )

  return facies.map(
    ({
      facies: globalFacies,
      previewProbability,
      id,
    }): GlobalFaciesSpecification => {
      let polygon = (rule.polygons as Polygon[]).find(
        (polygon): boolean => getId(polygon.facies) === id,
      )
      if (isEmpty(polygon) && isOverlayTruncationRule(rule)) {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        polygon = (Object.values(rule.overlay) as OverlayPolygon[]).find(
          (polygon): boolean => polygon.facies?.id === id,
        )
      }
      return {
        code: globalFacies.code,
        name: globalFacies.name,
        probability: Number(previewProbability) / cumulativeProbability,
        inZone: true,
        inRule: Object.is(polygon, undefined) ? -1 : (polygon as Polygon).order,
      }
    },
  )
}

function makeGaussianRandomFieldSpecification<
  T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends TruncationRule<T, S, P>,
>(rule: RULE): GaussianRandomFieldSpecification[] {
  return rule.fields.map((field): GaussianRandomFieldSpecification => {
    return {
      name: field.name,
      inZone: true,
      inRule: rule.fields.findIndex((item): boolean => item.id === field.id),
      inBackground: rule.isUsedInBackground(field),
    }
  })
}

function makeTruncationRuleSpecification<
  T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends TruncationRule<T, S, P>,
>(rule: RULE): TruncationRuleDescription<P> {
  return {
    type: rule.type,
    globalFaciesTable: makeGlobalFaciesTableSpecification(rule),
    gaussianRandomFields: makeGaussianRandomFieldSpecification(rule),
    values: rule.specification,
    // Not using constant parameters, is not implemented in the gui (yet)
    constantParameters: true,
  }
}

function hasCurrentParents<T extends Dependent>(item: T): boolean {
  const zoneStore = useZoneStore()
  const rootStore = useRootStore()
  if (!zoneStore.current) return false
  return hasParents(item, rootStore.parent.zone, rootStore.parent.region)
}

function parentId({ zone, region }: Parent): ID {
  if (region) {
    return uuidv5(getId(region), getId(zone))
  } else {
    return getId(zone)
  }
}

function sortAlphabetically<T extends Named>(arr: T[]): T[] {
  return Object.values(arr).sort((a, b): number => a.name.localeCompare(b.name))
}

const encodeState = (state: any): string => btoa(JSON.stringify(state))

export {
  getId,
  defaultSimulationSettings,
  makeSimplifiedTruncationRuleSpecification,
  makeTruncationRuleSpecification,
  hasCurrentParents,
  hasParents,
  parentId,
  getRandomInt,
  newSeed,
  allSet,
  isEmpty,
  notEmpty,
  sortAlphabetically,
  includes,
  identify,
  encodeState,
}
