import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed, reactive } from 'vue'
import { isArray } from 'lodash'

type PanelStructure = {
  selection: {
    zoneRegion: boolean
    facies: boolean
  }
  preview: {
    truncationRuleMap: boolean
    truncationRuleRealization: boolean
    gaussianRandomFields: boolean
    crossPlots: boolean
  }
  settings: {
    faciesProbability: boolean
    truncationRule: boolean
    gaussianRandomFields: boolean
    individualGaussianRandomFields: number[]
  }
}

export const usePanelStore = defineStore('panels', () => {
  const panels: PanelStructure = reactive({
    selection: {
      zoneRegion: false,
      facies: false,
    },
    preview: {
      truncationRuleMap: false,
      truncationRuleRealization: false,
      gaussianRandomFields: false,
      crossPlots: false,
    },
    settings: {
      faciesProbability: false,
      truncationRule: false,
      gaussianRandomFields: false,
      individualGaussianRandomFields: [],
    },
  })

  function $reset() {
    panels.selection.zoneRegion = false
    panels.selection.facies = false
    panels.preview.truncationRuleMap = false
    panels.preview.truncationRuleRealization = false
    panels.preview.gaussianRandomFields = false
    panels.preview.crossPlots = false
    panels.settings.faciesProbability = false
    panels.settings.truncationRule = false
    panels.settings.gaussianRandomFields = false
    panels.settings.individualGaussianRandomFields = []
  }

  function set<
    K1 extends string & keyof PanelStructure,
    K2 extends string & keyof PanelStructure[K1],
  >(
    sectionName: K1,
    panelName: K2 | undefined,
    open: number[] | boolean
  ) {
    if (!panelName) {
      for (const panelName in panels[sectionName]) {
        set(sectionName, panelName, open)
      }
    } else {
      const panel = panels[sectionName][panelName]
      if (panel === undefined) {
        return console.error("Can't find requested panel!", {
          panels,
          sectionName,
          panelName,
          panel,
        });
      }
      if (sectionName === 'settings' && panelName === 'individualGaussianRandomFields') {
        if (!isArray(open)) throw new Error('individual gaussian fields expects a list of numbers')
      }
      // @ts-ignore: We check the types are consistent above
      panels[sectionName][panelName] = open
    }
  }
  function open<
    K1 extends string & keyof PanelStructure,
    K2 extends string & keyof PanelStructure[K1],
  >(sectionName: K1, panelName?: K2) {
    set(sectionName, panelName, true)
  }
  function close<
    K1 extends string & keyof PanelStructure,
    K2 extends string & keyof PanelStructure[K1],
  >(sectionName: K1, panelName?: K2) {
    set(sectionName, panelName, false)
  }

  const getOpen = computed(() => {
    return (sectionName: keyof PanelStructure) =>
      Object.entries(panels[sectionName])
        .filter(([name, panel]) => typeof panel === 'boolean' ? panel : Object.values(panel).length > 0)
        .map(([name, panel]) => name)
  })
  function setOpen<
    S extends string & keyof PanelStructure,
    P extends string & keyof PanelStructure[S],
  >(sectionName: S, openPanels: string[]) {
    for (const panelName of Object.keys(panels[sectionName])) {
      // This one is special
      if (panelName === "individualGaussianRandomFields") continue;
      set(sectionName, panelName as P, openPanels.includes(panelName))
    }
  }

  function populate (panelSerialization: PanelStoreSerialization) {
    Object.assign(panels, panelSerialization)
  }

  const selection = computed({
    get: () => getOpen.value('selection'),
    set: (panels: string[]) => setOpen('selection', panels),
  })
  const preview = computed({
    get: () => getOpen.value('preview'),
    set: (panels: string[]) => setOpen('preview', panels),
  })
  const settings = computed({
    get: () => getOpen.value('settings'),
    set: (panels: string[]) => setOpen('settings', panels),
  })

  return {
    panels,
    set,
    open,
    close,
    getOpen,
    setOpen,
    selection,
    preview,
    settings,
    populate,
    $reset,
  }
})

export type PanelStoreSerialization = PanelStructure
export function usePanelStoreSerialization (): PanelStoreSerialization {
  const { panels } = usePanelStore()
  return panels
}

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(usePanelStore, import.meta.hot))
}
