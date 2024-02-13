import { v4 as uuidv4 } from 'uuid'
import type {
  BayfillSetting,
  CubicPolygonLevel,
  CubicPolygonSetting,
  FaciesReference,
  FieldChannelReference,
  FieldReference,
  NonCubicSetting,
  RuleOverlayTemplate,
  TruncationRuleTemplateFromJson,
} from '.'
import { getRelevant } from '@/stores/utils/helpers'
import type {
  Facies,
  Parent,
} from '@/utils/domain'
import {
  Bayfill,
  Cubic,
  CubicPolygon,
  NonCubic,
  OverlayPolygon
} from '@/utils/domain'
import type GaussianRandomField from '@/utils/domain/gaussianRandomField'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import { useOptionStore } from '@/stores/options'
import { useFaciesGroupStore } from '@/stores/facies/groups'
import { useFaciesStore } from '@/stores/facies'
import { makePolygonsFromSpecification } from '@/stores/truncation-rules/utils'
import type { TruncationRuleType } from '@/utils/domain/truncationRule/base'

export function processFields(
  fieldChannelReferences: FieldChannelReference[],
  parent: Parent,
): (GaussianRandomField | null)[] {
  const optionStore = useOptionStore()
  const fieldStore = useGaussianRandomFieldStore()
  const currentParentFields = getRelevant(fieldStore.available as GaussianRandomField[], parent)
  if (optionStore.options.automaticAlphaFieldSelection) {
    return fieldChannelReferences
      .map((fieldChannelReference) => {
        const field =
          currentParentFields[fieldChannelReference.field.index] ??
          currentParentFields.find(
            ({ name }) => name === fieldChannelReference.field.name,
          )

        return {
          channel: fieldChannelReference.channel,
          field: field ?? null,
        }
      })
      .sort((a, b) => a.channel - b.channel)
      .map(({ field }) => field)
  } else {
    return fieldChannelReferences.map((_) => null)
  }
}

export function processOverlay(
  overlayTemplates: RuleOverlayTemplate[],
  parent: Parent,
): OverlayPolygon[] {
  return overlayTemplates
    .flatMap(({ background, polygons }, index) => {
      return polygons.map(({ field, facies, probability, interval }) => {
        const id = uuidv4()
        const group = findOverlayGroup(background, parent)
        if (!group) {
          return null
        }
        return new OverlayPolygon({
          id,
          group,
          field: findField(field, parent),
          facies: findFacies(facies, parent),
          fraction: probability,
          center: interval,
          order: index,
        })
      })
    })
    .filter((item) => !!item) as OverlayPolygon[]
}

function findOverlayGroup(background: FaciesReference[], parent: Parent) {
  const faciesGroupStore = useFaciesGroupStore()
  const facies = background
    .map((faciesReference) => {
      const facies = findFacies(faciesReference, parent)
      if (!facies) {
        console.warn('Could not find facies by reference!', {
          faciesReference,
          parent,
        })
        return null
      }
      return facies
    })
    .filter((f) => !!f) as Facies[]
  const faciesGroup = faciesGroupStore.byFacies(facies, parent)
  if (!faciesGroup) {
    // TODO: Warn about this in RMS
    console.warn("Can't find overlay group!", { background, parent })
    return null
  }
  return faciesGroup
}

function findFacies(
  faciesReference: FaciesReference,
  parent: Parent,
): Facies | null {
  const faciesStore = useFaciesStore()
  const relevantFacies = getRelevant(faciesStore.available as Facies[], parent)
    .sort((a, b) => a.name.localeCompare(b.name))
  if (faciesReference.index >= 0) return relevantFacies[faciesReference.index] as Facies ?? null

  return (relevantFacies.find(({ name }) => name === faciesReference.name) ??
    null) as Facies | null
}

function findField(
  fieldReference: FieldReference,
  parent: Parent,
): GaussianRandomField | null {
  const fieldStore = useGaussianRandomFieldStore()
  const relevantFields = getRelevant(fieldStore.available as GaussianRandomField[], parent)

  return (relevantFields.find(({ name }) => name === fieldReference.name) ??
    relevantFields[fieldReference.index] ??
    null) as GaussianRandomField | null
}

export function processPolygons(
  template: TruncationRuleTemplateFromJson,
  parent: Parent,
  overlayPolygons: OverlayPolygon[] | null,
) {
  const optionStore = useOptionStore()
  const autoFill = optionStore.options.automaticFaciesFill
  const polygonReferences = processSettings(template)

  const polygonSpecifications = polygonReferences.map((polygon) => {
    if (!autoFill) return { ...polygon, facies: null }
    const facies = findFacies(polygon.facies, parent)
    return {
      ...polygon,
      facies: facies ?? null,
    }
  })

  const combination = [
    ...polygonSpecifications,
    ...(overlayPolygons ?? []).sort((a, b) => a.order - b.order),
  ]

  const structured = combination.map((polygon, index) => {
    if ('level' in polygon) {
      return {
        ...polygon,
        order: (polygon.level as CubicPolygonLevel).reduce(
          (order, level, index) => {
            // level is 1-indexed, 0 means "not in use"
            // index is 0-indexed (1 is added for multiplication)
            return level > 0 ? order + (level - 1) * (index + 1) : order
          },
          0,
        ),
      }
    } else {
      return {
        ...polygon,
        order: index,
      }
    }
  })

  const polygons = makePolygonsFromSpecification(structured)
  if (template.type === 'cubic') {
    return organizeCubicPolygons(
      polygons as (CubicPolygon | OverlayPolygon)[],
      structured.map((polygonSpec) =>
        'level' in polygonSpec
          ? (polygonSpec.level as CubicPolygonLevel)
          : null,
      ),
    )
  }

  return polygons
}

function processSettings(template: TruncationRuleTemplateFromJson) {
  const settings =
    template.type === 'cubic' ? template.settings.polygons : template.settings

  return template.polygons.map((polygon) => {
    const setting = (settings as (CubicPolygonSetting | BayfillSetting | NonCubicSetting)[]).find(
      (setting) =>
        setting.polygon === ('name' in polygon ? polygon.name : polygon.order),
    )
    if (setting) {
      return {
        ...setting,
        ...polygon,
      }
    } else {
      return polygon
    }
  })
}

function organizeCubicPolygons(
  polygons: (CubicPolygon | OverlayPolygon)[],
  levels: (CubicPolygonLevel | null)[],
): (CubicPolygon | OverlayPolygon)[] {
  const allPolygons = []
  if (polygons.length === 0) return polygons
  const root = new CubicPolygon({ order: -1 })
  for (let i = 0; i < levels.length; i++) {
    const polygon = polygons[i]
    if (polygon instanceof OverlayPolygon) {
      allPolygons.push(polygon)
    } else {
      const levelSpecification = levels[i]!
      let current = root
      for (let j = 0; j < levelSpecification.length; j++) {
        const level = levelSpecification[j]
        if (level <= 0) continue
        let polygon = current.children.find(({ order }) => order === level)
        if (!polygon) {
          if (
            j + 1 < levelSpecification.length &&
            levelSpecification[`${j + 1}`] > 0
          ) {
            polygon = new CubicPolygon({ parent: current, order: level })
          } else {
            polygon = polygons[i] as CubicPolygon
            polygon.order = level
            current.add(polygon)
          }
        }
        current = polygon
      }
    }
  }
  const queue = [root]
  while (queue.length > 0) {
    const current = queue.shift()!
    allPolygons.push(current)
    current.children.forEach((polygon) => {
      queue.push(polygon)
    })
  }
  return allPolygons
}

const typeMapping = {
  bayfill: Bayfill,
  'non-cubic': NonCubic,
  cubic: Cubic,
}

// From https://stackoverflow.com/questions/43481518/get-argument-types-for-function-class-constructor
type FirstArgument<T> = T extends (arg1: infer U, ...args: any[]) => any ? U : any;

export function makeRule<T extends TruncationRuleType>(
  type: T,
  args: FirstArgument<ConstructorParameters<(typeof typeMapping)[T]>>
) {
  const TruncationRule = typeMapping[type as keyof typeof typeMapping]
  if (!TruncationRule) {
    throw new Error(`The truncation rule of type ${type} is not implemented`)
  }
  return new TruncationRule(args)
}
