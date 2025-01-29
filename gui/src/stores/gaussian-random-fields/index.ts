import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed } from 'vue'
import type { Region, Zone } from '@/utils/domain'
import { GaussianRandomField } from '@/utils/domain'
import { defaultSimulationSettings, getId } from '@/utils'
import type { ID } from '@/utils/domain/types'
import type {
  GaussianRandomFieldSerialization,
  GaussianRandomFieldSpecification,
} from '@/utils/domain/gaussianRandomField'
import { Trend, Variogram } from '@/utils/domain/gaussianRandomField'
import { useZoneStore } from '@/stores/zones'
import { useRegionStore } from '@/stores/regions'
import { APSTypeError } from '@/utils/domain/errors'
import { newSeed as getNewSeed } from '@/utils/helpers'
import rms from '@/api/rms'
import {
  type GaussianRandomFieldCrossSectionStoreSerialization,
  useGaussianRandomFieldCrossSectionStore,
  useGaussianRandomFieldCrossSectionStoreSerialization,
} from './cross-sections'
import { useIdentifiedItems } from '@/stores/utils/identified-items'
import { useTruncationRuleStore } from '@/stores/truncation-rules'
import { resolveParentReference } from '@/stores/utils'
import { unpackVariogram } from '@/utils/domain/gaussianRandomField/variogram'
import { unpackTrend } from '@/utils/domain/gaussianRandomField/trend'
import type { SimulationSettings } from '@/utils/domain/bases/interfaces'
import { useParameterGridStore } from '@/stores/parameters/grid'
import { useParameterGridSimulationBoxStore } from '@/stores/parameters/grid/simulation-box'
import { useRootStore } from '@/stores'
import type { AvailableOptionSerialization } from '@/stores/parameters/serialization/helpers'
import type CrossSection from '@/utils/domain/gaussianRandomField/crossSection'
import { getRelevant } from '@/stores/utils/helpers'

export const useGaussianRandomFieldStore = defineStore(
  'gaussian-random-fields',
  () => {
    const store = useIdentifiedItems<GaussianRandomField>()
    const { available, identifiedAvailable, addAvailable, removeAvailable } =
      store

    const byId = computed(() => {
      return (id: ID | GaussianRandomField) =>
        identifiedAvailable.value[getId(id)]
    })

    const selected = computed(() => {
      const parent = useRootStore().parent

      return getRelevant(available.value, parent).sort((a, b) =>
        a.name > b.name ? 1 : -1,
      )
    })

    const simulationSettings = computed(() => {
      return (
        field?: GaussianRandomField,
        zone?: Zone | null,
      ): SimulationSettings & GaussianRandomField['settings'] => {
        const gridParameterStore = useParameterGridStore()
        const simBoxParameterStore = useParameterGridSimulationBoxStore()
        const zoneStore = useZoneStore()
        const grid = gridParameterStore
        const fieldSettings = field
          ? field.settings
          : ({
              gridModel: {
                use: false,
              },
              crossSection: { type: 'IJ' } as CrossSection,
              seed: -1,
            } as GaussianRandomField['settings'])
        zone = zone || (zoneStore.current as Zone)
        const globalSettings = gridParameterStore.waiting
          ? defaultSimulationSettings()
          : {
              gridAzimuth: grid.azimuth,
              gridSize: {
                ...(fieldSettings.gridModel?.use
                  ? fieldSettings.gridModel.size
                  : grid.size),
              },
              simulationBox: {
                ...simBoxParameterStore.size,
                z: zone
                  ? simBoxParameterStore.size.z instanceof Object
                    ? simBoxParameterStore.size.z[zone.code]
                    : simBoxParameterStore.size.z // Assuming it is a number
                  : 0,
              },
              simulationBoxOrigin: {
                ...simBoxParameterStore.origin,
              },
            }
        return {
          ...globalSettings,
          ...fieldSettings,
        }
      }
    })

    const specification = computed(() => {
      return (
        field: GaussianRandomField,
      ): GaussianRandomFieldSpecification => ({
        name: field.name,
        variogram: field.variogram,
        trend: field.trend,
        settings: {
          ...simulationSettings.value(field),
          ...field.settings,
        },
      })
    })

    function add(
      field: GaussianRandomField | GaussianRandomFieldSerialization,
    ) {
      if (!(field instanceof GaussianRandomField)) {
        const crossSectionStore = useGaussianRandomFieldCrossSectionStore()
        const variogram = new Variogram(unpackVariogram(field.variogram))
        const trend = new Trend(unpackTrend(field.trend))
        const crossSection = crossSectionStore.byId(
          field.settings.crossSection.id,
        )
        const parent = resolveParentReference(field.parent)

        field = new GaussianRandomField({
          ...field,
          variogram,
          trend,
          settings: { ...field.settings, crossSection },
          parent,
        })
      }
      addAvailable(field)
    }

    function populate(
      fields: (GaussianRandomField | GaussianRandomFieldSerialization)[],
    ) {
      for (const field of fields) add(field)
    }

    function newGaussianFieldName(zone: Zone, region: Region | null): string {
      const name = (num: number) => `GRF${num}`
      const relevant = getRelevant(available.value, { zone, region })

      let grfNumber = relevant.length + 1
      while (
        relevant.some((field): boolean => field.name === name(grfNumber))
      ) {
        grfNumber++
      }
      return name(grfNumber)
    }

    function addEmptyField(
      zone: Zone | null = null,
      region: Region | null = null,
    ) {
      const zoneStore = useZoneStore()
      const regionStore = useRegionStore()
      zone = zone ?? (zoneStore.current as Zone)
      region = region ?? (regionStore.current as Region | null)

      if (!zone) throw new APSTypeError("Zone can't be null in empty field.")

      const crossSectionStore = useGaussianRandomFieldCrossSectionStore()
      const crossSection = crossSectionStore.fetch(zone, region)

      const field = new GaussianRandomField({
        name: newGaussianFieldName(zone, region),
        crossSection,
        zone,
        region,
      })

      add(field)
      return field
    }

    function remove(field: GaussianRandomField) {
      const truncationRuleStore = useTruncationRuleStore()
      truncationRuleStore.deleteField(field)

      removeAvailable(field)
    }

    async function updateSimulation(field: GaussianRandomField) {
      if (field.waiting) {
        console.warn('already running')
        return
      }
      field.waiting = true

      try {
        field.simulation = await rms.simulateGaussianField({
          name: field.name,
          variogram: field.variogram,
          trend: field.trend,
          settings: simulationSettings.value(field),
        })
      } finally {
        field.waiting = false
      }
    }

    async function updateSimulations(
      fields: (GaussianRandomField | ID)[],
      all: boolean = false,
    ) {
      const _fields: GaussianRandomField[] = fields.map((field) =>
        typeof field === 'string' ? identifiedAvailable.value[field] : field,
      )
      const notSimulated = all
        ? _fields
        : _fields.filter((field) => !field.simulated)

      await Promise.all(notSimulated.map(updateSimulation))
    }

    function newSeed(field: GaussianRandomField) {
      field.settings.seed = getNewSeed()
    }

    function setProperty<
      VorTProp extends 'variogram' | 'trend',
      VorT extends VorTProp extends 'variogram' ? Variogram : Trend,
      P1 extends keyof VorT,
      P2 extends keyof VorT[P1],
    >(
      field: GaussianRandomField,
      variogramOrTrend: VorTProp,
      property: P1,
      subProperty: P2 | undefined,
      value: any,
    ) {
      const object = field[variogramOrTrend] as VorT
      if (subProperty !== undefined) {
        object[property][subProperty] = value
      } else {
        object[property] = value
      }
    }

    function $reset() {
      store.$reset()
      useGaussianRandomFieldCrossSectionStore().$reset()
    }

    return {
      available,
      identifiedAvailable,
      byId,
      selected,
      simulationSettings,
      specification,
      add,
      populate,
      $reset,
      addEmptyField,
      remove,
      updateSimulation,
      updateSimulations,
      newSeed,
      setProperty,
    }
  },
)

export type GaussianRandomFieldStoreSerialization =
  AvailableOptionSerialization<GaussianRandomFieldSerialization> & {
    crossSections: GaussianRandomFieldCrossSectionStoreSerialization
  }
export function useGaussianRandomFieldStoreSerialization(): GaussianRandomFieldStoreSerialization {
  const fieldsStore = useGaussianRandomFieldStore()
  return {
    available: fieldsStore.available.map((field) => field.toJSON()),
    crossSections: useGaussianRandomFieldCrossSectionStoreSerialization(),
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useGaussianRandomFieldStore, import.meta.hot),
  )
}
