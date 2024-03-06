import { acceptHMRUpdate, defineStore } from 'pinia'
import { useIdentifiedItems } from '@/stores/utils/identified-items'
import {
  CubicPolygon,
  NonCubicPolygon,
  OverlayPolygon,
} from '@/utils/domain'
import { computed } from 'vue'
import { getId, hasParents, makeTruncationRuleSpecification } from '@/utils'
import { useZoneStore } from '@/stores/zones'
import { useRegionStore } from '@/stores/regions'
import { useCopyPasteStore } from '@/stores/copy-paste'
import { useFaciesStore } from '@/stores/facies'
import { deserializePolygons, hasEnoughFacies, minFacies, normalizeOrder, resolveParentReference } from './utils';
import { Cubic, TruncationRule as BaseTruncationRule } from '@/utils/domain/truncationRule'
import type {
  InstantiatedTruncationRule,
  Facies,
  FaciesGroup,
  GaussianRandomField,
  Polygon,
  Region,
  Zone,
} from '@/utils/domain'
import type { TruncationRuleTemplateType } from '@/stores/truncation-rules/templates/types'
import { isNumber, sample, times } from 'lodash'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import { APSError, APSTypeError } from '@/utils/domain/errors'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import rms from '@/api/rms'
import { useTruncationRuleTemplateStore } from './templates'
import { useTruncationRulePresetStore } from './presets'
import { useFaciesGroupStore } from '@/stores/facies/groups'
import { useTruncationRuleTemplateTypeStore } from './templates/types'
import { makeRule } from './templates/utils'
import type { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import type { TruncationRuleSerialization } from '@/utils/domain/truncationRule/base'
import { getRelevant, isReady } from '@/stores/utils/helpers'
import type { ID } from '@/utils/domain/types'
import type { BayfillPolygonSerialization } from '@/utils/domain/polygon/bayfill'
import type { NonCubicPolygonSerialization } from '@/utils/domain/polygon/nonCubic'
import type { CubicPolygonSerialization } from '@/utils/domain/polygon/cubic'
import type { OverlayPolygonSerialization } from '@/utils/domain/polygon/overlay'

export interface RuleName {
  title: string
  disabled: boolean
  overlay: boolean
}

export function deserializeTruncationRule<S extends PolygonSerialization>(rule: TruncationRuleSerialization<S>, byId?: (field: ID) => GaussianRandomField) {
  if (!byId) {
    const gaussianRandomFieldStore = useGaussianRandomFieldStore()
    byId = gaussianRandomFieldStore.byId
  }
  return makeRule(rule.type, {
        ...rule,
        backgroundFields: rule.backgroundFields.map((field) =>
          field ? byId!(field) : null,
        ),
        polygons: deserializePolygons(rule.polygons),
        parent: resolveParentReference(rule.parent),
      })
}

export const useTruncationRuleStore = defineStore('truncation-rules', () => {
  const store = useIdentifiedItems<InstantiatedTruncationRule>()
  const { available, identifiedAvailable, addAvailable, removeAvailable } = store

  const current = computed(() => {
    const zoneStore = useZoneStore()
    const regionStore = useRegionStore()
    return available.value.find((rule) =>
      hasParents(rule, zoneStore.current! as Zone, regionStore.current as Region | null),
    ) ?? null
  })

  const ready = computed(() => {
    return <
      T extends Polygon,
      S extends PolygonSerialization,
      P extends PolygonSpecification,
      RULE extends BaseTruncationRule<T, S, P>,
    >(rule: RULE) => {
      const copyPasteStore = useCopyPasteStore()
      return !copyPasteStore.isPasting(rule.parent) &&
      isReady(rule)
    }
  })

  const relevant = computed(() => {
    const zoneStore = useZoneStore()
    const regionStore = useRegionStore()
    return available.value.filter(
      (rule) =>
        hasParents(rule, zoneStore.current! as Zone, regionStore.current as Region | null) &&
        hasEnoughFacies(rule),
    )
  })

  const ruleTypes = computed(() => {
    const templateTypeStore = useTruncationRuleTemplateTypeStore()
    return templateTypeStore.available
      .sort((a, b) => a.order - b.order)
      .map((rule) => ({
        title: rule.name,
        disabled: !hasEnoughFacies(rule),
        order: rule.order,
        value: rule.type,
      }))
  })

  const ruleNames = computed<RuleName[]>(() => {
    const templateStore = useTruncationRuleTemplateStore()
    const presetStore = useTruncationRulePresetStore()

    return templateStore.available
      .filter((template) => template.type === presetStore.type)
      .sort(
        (a, b) => minFacies(a) - minFacies(b) || a.name.localeCompare(b.name),
      )
      .map((template) => ({
        title: template.name,
        disabled: !hasEnoughFacies(template),
        overlay: 'overlay' in template && !!template.overlay,
      }))
  })

  function fetch() {
    const templateStore = useTruncationRuleTemplateStore()
    templateStore.fetch()
    useTruncationRulePresetStore()
      .fetch()
  }

  function add<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
  >(rule: BaseTruncationRule<T, S, P> | TruncationRuleTemplateType | InstantiatedTruncationRule) {
    if (!(rule instanceof BaseTruncationRule)) {
      rule = makeRule(rule.type, rule)
    }
    addAvailable(rule as InstantiatedTruncationRule)
  }

  function populate(
    rules: TruncationRuleSerialization<BayfillPolygonSerialization | NonCubicPolygonSerialization | CubicPolygonSerialization | OverlayPolygonSerialization>[],
  ) {
    const gaussianRandomFieldStore = useGaussianRandomFieldStore()

    for (const rule of rules) {
      addAvailable(deserializeTruncationRule(rule, gaussianRandomFieldStore.byId))
    }
  }

  function increaseOrderByRelativeTo<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends OverlayTruncationRule<T, S, P>
  >(
    rule: RULE,
    polygon: T,
    amount = 1,
  ) {
    for (const rulePolygon of rule.polygons) {
      if (
        !(rulePolygon instanceof CubicPolygon) &&
        rulePolygon.order >= polygon.order &&
        rulePolygon.overlay === polygon.overlay &&
        rulePolygon.atLevel === polygon.atLevel
      ) {
        rulePolygon.order = rulePolygon.order + amount
      }
    }
  }

  type AddPolygonOptions = {
    group?: string | FaciesGroup
    order?: number | null
    overlay?: boolean
    parent?: CubicPolygon | null
    atLevel?: number
  }
  function addPolygon<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends OverlayTruncationRule<T, S, P>,
  >(
    rule: RULE,
    {
      group = '',
      order = null,
      overlay = false,
      parent = null,
      atLevel = 0,
    }: AddPolygonOptions = {},
  ) {
    if (rule.type === 'bayfill')
      throw new Error('Bayfill must have exactly 5 polygons. Cannot add more.')

    if (!isNumber(order) || order < 0) {
      const polygons = rule.polygons.filter(
        (polygon) => polygon.overlay === overlay && polygon.atLevel === atLevel,
      )
      const maxOrder = polygons.reduce((max, p) => Math.max(p.order, max), 0)
      order = polygons.length === 0 ? 0 : maxOrder + 1
    }
    let polygon: NonCubicPolygon | CubicPolygon | OverlayPolygon | null = null
    if (overlay) {
      if (!(rule instanceof OverlayTruncationRule)) {
        throw new Error("Can't use Overlay without an OverlayTruncationRule")
      }
      let field: GaussianRandomField | null = null
      const groupPolygonCount = rule.overlayPolygons.filter(
        (polygon) => getId(polygon.group) === getId(group),
      ).length
      const gaussianRandomFieldStore = useGaussianRandomFieldStore()
      const availableFieldCount = gaussianRandomFieldStore.available.length
      if (
        groupPolygonCount + 1 >
        availableFieldCount - rule.backgroundFields.length
      ) {
        field = gaussianRandomFieldStore.addEmptyField(
          rule.parent.zone,
          rule.parent.region,
        )
      }

      const faciesGroupStore = useFaciesGroupStore()
      if (typeof group === 'string') {
        group = faciesGroupStore.identifiedAvailable[group]
      }
      polygon = new OverlayPolygon({ group, field, order })
    } else if (rule.type === 'non-cubic') {
      polygon = new NonCubicPolygon({ order })
    } else if (rule.type === 'cubic') {
      polygon = new CubicPolygon({ order, parent })
    } else {
      throw new APSTypeError('Invalid type')
    }
    increaseOrderByRelativeTo(rule as unknown as OverlayTruncationRule<OverlayPolygon | NonCubicPolygon | CubicPolygon, S, P>, polygon)
    rule.addPolygon(polygon as unknown as T)
    if (rule instanceof Cubic) {
      normalizeOrder(rule, (polygon, order) => {
        polygon.order = order
      })
    }
  }

  function removePolygon<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends OverlayTruncationRule<T, S, P>,
  >(
    rule: RULE,
    polygon: T,
  ) {
    rule.removePolygon(polygon)

    if (polygon instanceof CubicPolygon) {
      const parent = polygon.parent
      if (parent) {
        const childIndex = parent.children.findIndex(
          (child) => child.id === polygon.id,
        )
        if (childIndex !== -1) parent.children.splice(childIndex, 1)
      }
    }

    increaseOrderByRelativeTo(rule, polygon, -1)
    const faciesGroupStore = useFaciesGroupStore()

    if (
      polygon.facies &&
      !rule.backgroundPolygons
        .map((background) => getId(background.facies))
        .includes(getId(polygon.facies))
    ) {
      const group = faciesGroupStore.available.find(
        (group) => polygon.facies && group.has(polygon.facies),
      )

      if (group) {
        const facies = group.facies.filter((f) => f !== polygon.facies)
        if (facies.length > 0) {
          faciesGroupStore.update(group as FaciesGroup, facies as Facies[])
        } else {
          const groupPolygons = rule.overlayPolygons.filter(
            (p) => getId(p.group) === getId(group),
          )
          for (const groupPolygon of groupPolygons) {
            rule.removePolygon(groupPolygon)
          }
          faciesGroupStore.remove(group as FaciesGroup)
        }
      }
    }

    // Remove lingering FaciesGroup (if overlay)
    if (polygon instanceof OverlayPolygon) {
      const group = faciesGroupStore.identifiedAvailable[polygon.group.id]
      if (
        rule.overlayPolygons.filter((p) => p.group.id === group.id).length === 0
      ) {
        faciesGroupStore.remove(group)
      }
    }

    // Normalize probabilities again
    normalizeProportionFactors(rule)
  }

  function split(rule: Cubic, polygon: CubicPolygon, splitCount: number) {
    times(splitCount, (index) =>
      addPolygon(rule, { parent: polygon, order: index + 1 }),
    )
  }

  function merge(rule: Cubic, polygons: CubicPolygon[]) {
    const parent = sample(polygons.map((p) => p.parent))
    if (!parent) throw new Error('Must merge at least one polygon.')
    if (!polygons.every((polygon) => getId(polygon.parent) === getId(parent))) {
      throw new APSTypeError(
        'Polygons need to all have the same parent in order to be merged',
      )
    }
    polygons.forEach((polygon) => removePolygon(rule, polygon))
    if (parent.children.length !== 0) {
      addPolygon(rule, { parent, atLevel: parent.atLevel + 1 })
    }
  }

  function changeOrder<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends BaseTruncationRule<T, S, P>,
  >(
    rule: RULE,
    polygon: Polygon,
    direction: number,
  ) {
    const other = rule.polygons.find(
      (p) => p.order === polygon.order + direction,
    )
    if (other && !(other instanceof CubicPolygon)) {
      other.order = polygon.order
    }
    polygon.order += direction
  }

  async function updateRealization<
      T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends BaseTruncationRule<T, S, P>,
  >(rule: RULE) {
    const faciesStore = useFaciesStore()
    faciesStore.normalize()

    const fieldStore = useGaussianRandomFieldStore()

    const { faciesMap, fields } = await rms.simulateRealization(
      rule.fields.map((field) => fieldStore.specification(field)),
      makeTruncationRuleSpecification(rule),
    )

    rule.realization = faciesMap

    fields.forEach((field) => {
      const ruleField = rule.fields.find((item) => item.name === field.name)
      if (ruleField) {
        ruleField.simulation = field.data
      }
    })
  }

  function deleteField(field: GaussianRandomField) {
    available.value
      .filter((rule) => rule.fields.some((grf) => grf.id === field.id))
      .forEach((rule) => {
        if (rule.isUsedInBackground(field)) {
          updateBackgroundField(
            rule,
            rule.backgroundFields.indexOf(field),
            null,
          )
        } else {
          const overlayPolygons = (rule.polygons as Array<Polygon>).filter(
            (p) => p instanceof OverlayPolygon,
          ) as OverlayPolygon[]
          overlayPolygons
            .filter((p) => getId(p.field) === getId(field))
            .forEach((p) => { p.field = null })
        }
      })
  }

  function updateBackgroundField<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends BaseTruncationRule<T, S, P>,
  >(
    rule: RULE,
    index: number,
    field: GaussianRandomField | null,
  ) {
    if (index < 0 || index >= rule.backgroundFields.length) {
      throw new APSError(
        `The index (${index}) is outside the range of the background fields in the truncation rule with ID ${rule.id}`,
      )
    }
    rule.backgroundFields.splice(index, 1, field)
  }

  function updateFacies<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends BaseTruncationRule<T, S, P>,
  >(
    rule: RULE,
    polygon: Polygon,
    facies: Facies,
  ) {
    polygon.facies = facies

    if (facies && !facies.previewProbability) {
      facies.previewProbability = polygon.fraction
    }
    normalizeProportionFactors(rule)
  }

  function toggleOverlay<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends OverlayTruncationRule<T, S, P>,
>(rule: RULE, value: boolean) {
    const fieldStore = useGaussianRandomFieldStore()
    // If there are too few GRFs, add more
    const availableFields = getRelevant(fieldStore.available as GaussianRandomField[], rule.parent)
    if (availableFields.length <= rule.backgroundFields.length) {
      fieldStore.addEmptyField(rule.parent.zone, rule.parent.region)
    }

    rule.useOverlay = value
  }

  function normalizeProportionFactors<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends BaseTruncationRule<T, S, P>,
  >(rule: RULE) {
    const proportional = false
    const facies = rule.polygons.reduce((obj, polygon) => {
      const id = getId(polygon.facies)
      if (id) {
        if (!obj.has(id)) obj.set(id, [])
        obj.get(id)!.push(polygon)
      }
      return obj
    }, new Map<string, Polygon[]>())

    for (const polygons of facies.values()) {
      const sum = polygons.reduce((sum, polygon) => sum + polygon.fraction, 0)
      if (sum === 1) continue
      for (const polygon of polygons) {
        polygon.fraction =
          isNumber(polygon.fraction) && polygon.fraction > 0 && proportional
            ? polygon.fraction / sum
            : 1 / polygons.length
      }
    }

    const faciesStore = useFaciesStore()
    faciesStore.selected
      .map((f) => rule.polygons.filter((p) => getId(p.facies) === getId(f)))
      .filter((polygonList) => polygonList.length === 1)
      .map((polygonList) => polygonList[0])
      .forEach((polygon) => (polygon.fraction = 1))
  }

  function $reset() {
    useTruncationRulePresetStore()
      .$reset()
    useTruncationRuleTemplateStore()
      .$reset()
    store.$reset()
  }

  return {
    available,
    identifiedAvailable,
    current,
    ready,
    relevant,
    ruleTypes,
    ruleNames,
    fetch,
    add,
    remove: removeAvailable,
    populate,
    $reset,
    increaseOrderByRelativeTo,
    addPolygon,
    removePolygon,
    split,
    merge,
    changeOrder,
    updateRealization,
    deleteField,
    updateBackgroundField,
    updateFacies,
    toggleOverlay,
    normalizeProportionFactors,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useTruncationRuleStore, import.meta.hot),
  )
}
