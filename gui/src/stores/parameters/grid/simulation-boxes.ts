import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed, ref } from 'vue'
import rms from '@/api/rms'
import type { SimulationBoxSize as RmsSimulationBoxSize } from '@/api/types'
import type GridModel from '@/utils/domain/gridModel'
import { displayWarning } from '@/utils/helpers/storeInteraction'

type SimulationBoxes = Record<string, Record<'true' | 'false', RmsSimulationBoxSize | null>>

export type SimulationBoxesStoreSerialization = {
    rough: boolean
    simulationBoxes: SimulationBoxes
}

export const useParameterGridSimulationBoxesStore = defineStore(
  'parameter-grid-simulation-boxes',
  () => {

    const rough = ref(false)
    const waiting = ref(false)

    const _simulationBoxes = ref<SimulationBoxes>({})

    function $reset() {
      rough.value = false
      waiting.value = false
      _simulationBoxes.value = {}
    }

    async function updateSimulationBox (gridModel: GridModel | null) {
        const roughKey = rough.value ? 'true' : 'false'

        if (!gridModel) return;
        if (!_simulationBoxes.value[gridModel.name]) {
            _simulationBoxes.value[gridModel.name] = {
                'true': null,
                'false': null,
            }
        }
        waiting.value = true
        try {
            if (!_simulationBoxes.value[gridModel.name][roughKey]) {
              setTimeout(async () => {
                if (waiting.value) {
                  const rmsVersion = await rms.rmsVersion()
                  if (rmsVersion < '14.1') {
                    displayWarning(`It's taking a while to compute the simulation box thickness.\nConsider using RMS 14.1 or newer, as it includes functionality for fetching the thickness directly`)
                  }
                }
              }, 5_000)
                _simulationBoxes.value[gridModel.name][roughKey] = await rms.simulationBoxOrigin(gridModel.name, rough.value)
            }
        } finally {
            waiting.value = false
        }
      }
      const simulationBoxes = computed(() => _simulationBoxes.value)

    function populate (data: SimulationBoxesStoreSerialization) {
        rough.value = data.rough
        _simulationBoxes.value = data.simulationBoxes
    }

    return {
        rough,
        waiting,
        updateSimulationBox,
        simulationBoxes,
        populate,
        $reset,
    }
  },
)

export function useSimulationBoxesStoreSerialization(): SimulationBoxesStoreSerialization {
    const { rough, simulationBoxes } = useParameterGridSimulationBoxesStore()
    return {
        rough,
        simulationBoxes,
    }
}


if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterGridSimulationBoxesStore, import.meta.hot),
  )
}
