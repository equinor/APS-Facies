import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import type { Parent, Zone, Region } from '@/utils/domain'
import type { ZoneStoreSerialization } from './zones'
import { useZoneStoreSerialization, useZoneStore } from './zones'
import { type RegionStoreSerialization, useRegionStore, useRegionStoreSerialization } from './regions'
import { type GridModelStoreSerialization, useGridModelStoreSerialization, useGridModelStore } from './grid-models'
import { type OptionStoreSerialization, useOptionStoreSerialization, useOptionStore } from './options'
import { type ConstantStoreSerialization, useConstantsStore, useConstantStoreSerialization } from './constants'
import {
  useTruncationRuleStore,
} from './truncation-rules'
import { useParameterStore } from './parameters'
import { useFmuOptionStore } from './fmu/options'
import {
  useGlobalFaciesStore,
} from './facies/global'
import migrate from './utils/migration'
import { type CopyPasteStoreSerialization, useCopyPaseSerialization, useCopyPasteStore } from './copy-paste'
import { type FmuStoreSerialization, useFmuStoreSerialization } from './fmu/serialization'
import { type ParameterStoreSerialization, useParameterStoreSerialization } from './parameters/serialization';
import { displayError } from '@/utils/helpers/storeInteraction'
import { useConstantsFaciesColorsStore } from '@/stores/constants/facies-colors'
import { type FaciesStoreSerialization, useFaciesStoreSerialization } from '@/stores/facies/serialization'
import { useFaciesStore } from '@/stores/facies'
import { useFaciesGroupStore } from '@/stores/facies/groups'
import {
  type GaussianRandomFieldStoreSerialization,
  useGaussianRandomFieldStore,
  useGaussianRandomFieldStoreSerialization
} from '@/stores/gaussian-random-fields'
import { useGaussianRandomFieldCrossSectionStore } from '@/stores/gaussian-random-fields/cross-sections'
import {
  type TruncationRuleStoreSerialization,
  useTruncationRuleStoreSerialization
} from '@/stores/truncation-rules/serialization'
import { useTruncationRulePresetStore } from '@/stores/truncation-rules/presets'
import type { PanelStoreSerialization } from '@/stores/panels'
import { usePanelStore, usePanelStoreSerialization } from '@/stores/panels'
import type { RmsJob } from '@/plugins/rms'
import { useFmuMaxDepthStore } from '@/stores/fmu/maxDepth'
import { useMessageStore } from '@/stores/messages'

export type RootStoreSerialization = {
  version: string
  copyPase: CopyPasteStoreSerialization
  // message,
  panels: PanelStoreSerialization
  gridModels: GridModelStoreSerialization
  zones: ZoneStoreSerialization
  regions: RegionStoreSerialization
  facies: FaciesStoreSerialization
  fmu: FmuStoreSerialization
  gaussianRandomFields: GaussianRandomFieldStoreSerialization
  truncationRules: TruncationRuleStoreSerialization
  parameters: ParameterStoreSerialization
  constants: ConstantStoreSerialization
  options: OptionStoreSerialization
  // modelFileLoader,
  // modelFileExporter,

}

export const useRootStore = defineStore('root', () => {
  const version = '1.14.0'
  const _loaded = reactive({ value: false, loading: false })
  const _loading = reactive({ value: false, message: '' })

  const loaded = computed(() => _loaded.value)
  const loading = computed(() => _loading.value)
  const loadingMessage = computed({
    get: () => _loading.message,
    set: (message: string) => _loading.message = message
  })
  const mayLoadParameters = computed(() => !(_loaded.value || _loaded.loading))

  // Various checks used throughout the app
  const canSpecifyModelSettings = computed(() => {
    const zoneStore = useZoneStore()
    const regionStore = useRegionStore()
    if (regionStore.use) {
      return !!zoneStore.current && !!regionStore.current
    }
    return !!zoneStore.current
  })

  const parent = computed<Parent>(() => {
    const zoneStore = useZoneStore()
    const regionStore = useRegionStore()
    return { zone: zoneStore.current as Zone, region: regionStore.current as Region | null }
  })

  async function fetch() {
    if (!mayLoadParameters.value) return

    const wasLoading = _loading.value
    _loading.value = true

    await Promise.all([
      useGridModelStore().fetch(),
      useConstantsStore().fetch(),
      useTruncationRuleStore().fetch(),
      useParameterStore().fetch(),
    ])

    _loading.value = wasLoading
    _loaded.value = true
  }

  async function refresh(
    payload: string | { message?: string; force?: boolean },
  ) {
    const wasLoading = _loading.value
    if (typeof payload === 'string') {
      payload = { message: payload, force: false }
    }

    if (!loading.value && !payload.force) return

    _loading.value = true
    _loading.message = payload.message ?? ''

    await Promise.all([
      useGridModelStore().refresh(),
      useGlobalFaciesStore().refresh(),
    ])

    _loading.value = wasLoading
    _loading.message = ''
  }

  function updateProgressMessage(restoring: string) {
    _loading.message = `Restoring ${restoring}`
  }

  async function populate(data: RootStoreSerialization | RmsJob) {
    $reset()
    data = await migrate(data, version) // see migration
    startLoading('Populating store')

    try {
      await fetch()

      if (data.gridModels) {
        updateProgressMessage('grid models')

        const gridModelStore = useGridModelStore();
        gridModelStore.populate(data.gridModels.available);
        if (data.gridModels.current) {
          await gridModelStore.select(data.gridModels.current, false);
        }
      }
      if (data.parameters) {
        updateProgressMessage('parameters')
        await useParameterStore()
          .populate(data.parameters)
      }
      // Options
      if (data.options) {
        updateProgressMessage('options')
        useOptionStore()
            .populate(data.options)
      }

      // FMU options
      if (data.fmu) {
        updateProgressMessage('FMU options')
        useFmuOptionStore()
            .populate(data.fmu)
      }

      // Zones
      if (data.zones) {
        updateProgressMessage('zones')
        const { available, current } = data.zones
        const zoneStore = useZoneStore()
        zoneStore.populate(available)
        if (
          current &&
          available.find((z) => z.id === current)
        ) {
          zoneStore.setCurrentId(current)
        }
      }

      if (data.regions) {
        updateProgressMessage('regions')
        useRegionStore()
          .populate(data.regions)
      }

    // Color Library
    if (data.constants) {
      const { faciesColors } = data.constants
        updateProgressMessage('facies color pallet')
      useConstantsFaciesColorsStore()
          .populate(faciesColors.available, faciesColors.current);
    }

    // Facies
    if (data.facies) {
        updateProgressMessage('Facies')
      const faciesStore = useFaciesStore()
      useGlobalFaciesStore()
          .populate(data.facies.global.available)
      faciesStore
          .populate(data.facies.available)
      useFaciesGroupStore()
          .populate(data.facies.groups.available)
      faciesStore
          .populateConstantProbability(data.facies.constantProbability)
    }

    // Gaussian Random Fields
    if (data.gaussianRandomFields) {
      updateProgressMessage('Gaussian Random Fields')
      useGaussianRandomFieldCrossSectionStore()
          .populate(data.gaussianRandomFields.crossSections.available)
      useGaussianRandomFieldStore()
          .populate(data.gaussianRandomFields.available)
    }

    // Truncation rules
    if (data.truncationRules) {
      updateProgressMessage('Truncation rules')
      const { type, template } = data.truncationRules.preset
      useTruncationRulePresetStore()
          .populate(type, template)
      useTruncationRuleStore()
          .populate(data.truncationRules.available)
    }

    // Reopen the different panels
    if (data.panels) {
      updateProgressMessage('opened panels')
      usePanelStore()
          .populate(data.panels)
    }

    // Make sure the available data is up to date
    await refresh({
      message: 'Refreshing data from RMS',
      force: true,
    })

    } catch (e) {
      displayError(String(e))
      console.error('failed', e)
    } finally {
      finishLoading()
    }
  }

  function startLoading(message?: string) {
    _loading.value = true
    _loading.message = message ?? 'Loading job. Please wait.'
  }

  function finishLoading() {
    _loading.value = false
    _loading.message = ''
  }

  function $reset() {
    _loaded.value = false
    _loaded.loading = false
    _loading.value = false
    _loading.message = ''
    for (const useStore of [
      useFaciesStore,
      useFmuMaxDepthStore,
      useFmuOptionStore,
      useGaussianRandomFieldStore,
      useParameterStore,
      useTruncationRuleStore,
      useCopyPasteStore,
      useGridModelStore,
      useMessageStore,
      useOptionStore,
      usePanelStore,
      useRegionStore,
      useZoneStore,
    ]) {
      useStore()
        .$reset()
    }
  }

  return {
    version,
    loaded,
    loading,
    loadingMessage,
    mayLoadParameters,
    canSpecifyModelSettings,
    parent,
    fetch,
    refresh,
    populate,
    startLoading,
    finishLoading,
    $reset,
  }
})

export function useStateSerialization(): RootStoreSerialization {
  const rootStore = useRootStore()
  return {
    version: rootStore.version,
    copyPase: useCopyPaseSerialization(),
    // message,
    panels: usePanelStoreSerialization(),
    gridModels: useGridModelStoreSerialization(),
    zones: useZoneStoreSerialization(),
    regions: useRegionStoreSerialization(),
    facies: useFaciesStoreSerialization(),
    fmu: useFmuStoreSerialization(),
    gaussianRandomFields: useGaussianRandomFieldStoreSerialization(),
    truncationRules: useTruncationRuleStoreSerialization(),
    parameters: useParameterStoreSerialization(),
    constants: useConstantStoreSerialization(),
    options: useOptionStoreSerialization(),
    // modelFileLoader,
    // modelFileExporter,
  }
}


if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useRootStore, import.meta.hot))
}
