import { acceptHMRUpdate, defineStore } from 'pinia'
import _truncationRules from './truncationRules.json'
import _simpleTruncationRules from './simpleTruncationRules.json'
import type { TruncationRuleTemplateType } from '@/stores/truncation-rules/templates/types'
import { Bayfill } from '@/utils/domain'
import type {
  Facies,
  FaciesGroup,
  Parent,
  Polygon,
  GaussianRandomField,
} from '@/utils/domain'
import { useZoneStore } from '@/stores/zones'
import { useRegionStore } from '@/stores/regions'
import { APSError } from '@/utils/domain/errors'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import { useFaciesStore } from '@/stores/facies'
import { sortAlphabetically } from '@/utils'
import { useTruncationRuleTemplateTypeStore } from './types'
import { useOptionStore } from '@/stores/options'
import { useFaciesGroupStore } from '@/stores/facies/groups'
import {
  makeRule,
  processFields,
  processOverlay,
  processPolygons,
} from './utils'
import type { FmuUpdatableSerialization } from '@/utils/domain/bases/fmuUpdatable'
import { ref } from 'vue'
import type { TruncationRuleType } from '@/utils/domain/truncationRule/base'
import { Orientation } from '@/utils/domain/truncationRule/cubic'
import { useTruncationRuleStore } from '@/stores/truncation-rules'
import { getRelevant } from '@/stores/utils/helpers'

export type FaciesReference = {
  name: string
  index: number
}

export type NamedPolygonReference = {
  name: string
  facies: FaciesReference
  proportion: number
}
export type OrderedPolygonReference = {
  order: number
  facies: FaciesReference
  proportion: number
}

export type FieldReference = {
  name: string
  index: number
}
export type FieldChannelReference = {
  channel: number
  field: FieldReference
}

export type BayfillSetting = {
  name: string
  polygon: string
  slantFactor: FmuUpdatableSerialization
}

export type BayfillRuleTemplate = {
  name: string
  type: 'bayfill'
  minFields: number
  polygons: NamedPolygonReference[]
  settings: BayfillSetting[]
  fields: FieldChannelReference[]
}

export type RuleOverlayPolygon = {
  field: FieldReference
  facies: FaciesReference
  probability: number
  interval: number
}

export type RuleOverlayTemplate = {
  polygons: RuleOverlayPolygon[]
  background: FaciesReference[]
}

export type NonCubicSetting = {
  angle: FmuUpdatableSerialization
  polygon: number
  fraction: number
}

export type NonCubicRuleTemplate = {
  name: string
  type: 'non-cubic'
  minFields: number
  polygons: OrderedPolygonReference[]
  settings: NonCubicSetting[]
  fields: FieldChannelReference[]
  overlay?: RuleOverlayTemplate[]
}

export type CubicPolygonLevel = [number, number, number]
export type CubicPolygonSetting = {
  polygon: number
  fraction: number
  level: CubicPolygonLevel
}

export type CubicSettings = {
  direction: 'H' | 'V'
  polygons: CubicPolygonSetting[]
}

export type CubicRuleTemplate = {
  name: string
  type: 'cubic'
  minFields: number
  polygons: OrderedPolygonReference[]
  settings: CubicSettings
  fields: FieldChannelReference[]
  overlay?: RuleOverlayTemplate[]
}

export type TruncationRuleTemplateFromJson =
  | BayfillRuleTemplate
  | NonCubicRuleTemplate
  | CubicRuleTemplate

export function isBayfillRuleTemplate(
  template: TruncationRuleTemplateFromJson,
): template is BayfillRuleTemplate {
  return template.type === 'bayfill'
}
export function isNonCubicRuleTemplate(
  template: TruncationRuleTemplateFromJson,
): template is NonCubicRuleTemplate {
  return template.type === 'non-cubic'
}
export function isCubicRuleTemplate(
  template: TruncationRuleTemplateFromJson,
): template is CubicRuleTemplate {
  return template.type === 'cubic'
}

type SimpleTruncationRuleJson = {
  templates: TruncationRuleTemplateFromJson[]
}
type TruncationRuleJson = {
  types: TruncationRuleTemplateType[]
  templates: TruncationRuleTemplateFromJson[]
}

export const truncationRules = _truncationRules as TruncationRuleJson
export const simpleTruncationRules =
  _simpleTruncationRules as SimpleTruncationRuleJson

export const useTruncationRuleTemplateStore = defineStore(
  'truncation-rule-templates',
  () => {
    const available = ref<TruncationRuleTemplateFromJson[]>([])

    function fetch() {
      const typeStore = useTruncationRuleTemplateTypeStore()
      typeStore.fetch()

      available.value = [
        // Don't show overlay templates in production, where users are experts
        // who want to configure these themselves.
        ...truncationRules.templates,
        ...simpleTruncationRules.templates,
      ]
    }

    function populate(templates: TruncationRuleTemplateFromJson[]) {
      const typeStore = useTruncationRuleTemplateTypeStore()
      typeStore.populate(typeStore.available)
      available.value = templates
    }

    function createRule(
      name: string,
      type: TruncationRuleType,
      parent: Parent | null = null,
    ) {
      const optionStore = useOptionStore()
      const zoneStore = useZoneStore()
      const regionStore = useRegionStore()
      const fieldStore = useGaussianRandomFieldStore()
      const faciesStore = useFaciesStore()
      const faciesGroupStore = useFaciesGroupStore()
      const ruleStore = useTruncationRuleStore()

      const autoFill = optionStore.options.automaticFaciesFill

      parent =
        parent ??
        ({
          zone: zoneStore.current!,
          region: regionStore.current,
        } as Parent)

      const template = available.value.find(
        (template) => template.name === name && template.type === type,
      )
      if (!template)
        throw new APSError('No template with the given name and type')
      const missing =
        template.minFields -
        getRelevant(fieldStore.available as GaussianRandomField[], parent)
          .length
      for (let i = 0; i < missing; i++) {
        fieldStore.addEmptyField()
      }

      const groups = faciesGroupStore.available.filter((group) =>
        group.isChildOf(parent!),
      )
      for (const group of groups) {
        faciesGroupStore.remove(group as FaciesGroup)
      }

      if (autoFill && !isBayfillRuleTemplate(template) && template.overlay) {
        const selectedFacies = sortAlphabetically(faciesStore.selected)
        template.overlay.forEach((item) =>
          faciesGroupStore.get(
            /* creates new if none is found */
            item.background.map((facies) => selectedFacies[facies.index]),
            parent!,
          ),
        )
      }

      const backgroundFields = processFields(template.fields, parent)
      const overlayPolygons =
        !isBayfillRuleTemplate(template) && template.overlay
          ? processOverlay(template.overlay, parent)
          : null

      const polygons = processPolygons(template, parent, overlayPolygons)

      const uniqueFacies = [
        ...polygons.reduce(
          (faciesSet, polygon) =>
            polygon.facies ? faciesSet.add(polygon.facies) : faciesSet,
          new Set<Facies>(),
        ),
      ]
      const hasSetProbabilities = uniqueFacies.some(
        ({ previewProbability }) =>
          !!previewProbability || previewProbability === 0,
      )
      if (!hasSetProbabilities) {
        uniqueFacies.forEach((facies) => {
          facies.previewProbability = 1 / uniqueFacies.length
        })
      }

      if (uniqueFacies.length === 0) {
        // This is a simple template, without any facies specification
        // However, at least two facies HAS to be selected in order to create a truncation rule
        faciesStore.normalize()
      }

      function getDirection(
        settings: BayfillSetting[] | NonCubicSetting[] | CubicSettings,
      ) {
        const mapping = {
          H: Orientation.HORIZONTAL,
          V: Orientation.VERTICAL,
        }
        if (!('direction' in settings)) return null
        return mapping[settings.direction]
      }
      const direction = getDirection(template.settings)

      const rule = makeRule(type, {
        direction,
        polygons,
        backgroundFields,
        overlay: {
          use: overlayPolygons ? overlayPolygons.length > 0 : false,
        },
        name,
        ...parent,
      })

      ruleStore.add(rule)

      if (
        uniqueFacies.length > 0 &&
        faciesStore.selected.length > uniqueFacies.length &&
        !(rule instanceof Bayfill)
      ) {
        // That is, we have more facies available than what the template requires,
        // so we enable overlay
        ruleStore.toggleOverlay(rule, true)
      }

      function normalizeProportions(polygons: Polygon[]) {
        const probabilityFacies = polygons.map((polygon) => ({
          facies: polygon.facies,
          probability:
            'proportion' in polygon && typeof polygon.proportion === 'number'
              ? polygon.proportion
              : 1,
        }))
        probabilityFacies.forEach(({ facies, probability }) => {
          if (facies) facies.previewProbability = probability
        })
      }

      if (autoFill && faciesStore.unset) {
        normalizeProportions(polygons)
      }
    }

    function $reset() {
      available.value = []
    }

    return {
      available,
      fetch,
      populate,
      createRule,
      $reset,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useTruncationRuleTemplateStore, import.meta.hot),
  )
}
