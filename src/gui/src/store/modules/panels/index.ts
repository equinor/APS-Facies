import Vue from 'vue'

import { PanelsState } from '@/store/modules/panels/typing'
import APSTypeError from '@/utils/domain/errors/type'
import { Module } from 'vuex'
import { Context as RootContext, RootState } from '@/store/typing'
import { isNumber } from 'lodash'

type Context = RootContext<PanelsState, RootState>

interface Panel {
  order: number
  actions: ((context: Context) => Promise<void>)[]
}

class Panels {
  private readonly _panels: {
    selection: {
      zoneRegion: Panel
      facies: Panel
    }
    preview: {
      truncationRuleMap: Panel
      truncationRuleRealization: Panel
      gaussianRandomFields: Panel
      crossPlots: Panel
    }
    settings: {
      faciesProbability: Panel
      truncationRule: Panel
      gaussianRandomFields: Panel
    }
  }

  public constructor () {
    this._panels = {
      selection: {
        zoneRegion: {
          order: 0,
          actions: [],
        },
        facies: {
          order: 1,
          actions: [],
        },
      },
      preview: {
        truncationRuleMap: {
          order: 0,
          actions: [],
        },
        truncationRuleRealization: {
          order: 1,
          actions: [],
        },
        gaussianRandomFields: {
          order: 2,
          actions: [
            async ({ dispatch, rootGetters }): Promise<void> => { await dispatch('gaussianRandomFields/updateSimulations', { fields: rootGetters.fields }, { root: true }) },
          ],
        },
        crossPlots: {
          order: 3,
          actions: [],
        },
      },
      settings: {
        faciesProbability: {
          order: 0,
          actions: [],
        },
        truncationRule: {
          order: 1,
          actions: [],
        },
        gaussianRandomFields: {
          order: 2,
          actions: [],
        },
      }
    }
  }

  public get selection (): string[] { return this.getNames('selection') }
  public get preview (): string[] { return this.getNames('preview') }
  public get settings (): string[] { return this.getNames('settings') }

  public async doActions (context: Context, type: string, panel: string): Promise<void> {
    await Promise.all(
      (this._panels[`${type}`][`${panel}`] as Panel).actions
        .map((action): Promise<void> => action(context))
    )
  }

  private getNames (name: string): string[] {
    const panels = this._panels[`${name}`]
    return Object.keys(panels)
      .sort((a, b): number => panels[`${a}`].order - panels[`${b}`].order)
  }
}

const PANELS = new Panels()

function hasPanel (type: string, panel: string | undefined = undefined): boolean {
  if (PANELS[`${type}`] !== undefined) {
    return panel
      ? PANELS[`${type}`].includes(panel)
      : true
  } else {
    return false
  }
}

function getIndices (state: PanelsState, type: Section): number[] {
  return PANELS[type]
    .map((panel, index): [boolean, number] => [state[`${type}`][`${panel}`], index])
    .filter(([toggled, _]): boolean => toggled || isNumber(toggled))
    .map(([_, index]): number => index)
}

type Section = 'selection' | 'preview' | 'settings'

interface Specification<T=string> {
  type: Section
  panel: T
}

interface FullSpecification<T=string> extends Specification<T> {
  toggled: boolean
}

type Payload = Section | Specification<string | string[]>

async function _change (context: Context, type: string, panel: string, toggled: boolean | number): Promise<void> {
  context.commit('CHANGE', { type, panel, toggled })
  await PANELS.doActions(context, type, panel)
}

async function changePanel (context: Context, payload: Payload, toggled: boolean | number): Promise<void> {
  if (typeof payload === 'string') {
    if (hasPanel(payload)) {
      for (const panel of PANELS[`${payload}`]) {
        await _change(context, payload, panel, toggled)
      }
    } else {
      throw new APSTypeError(`'${payload}' is not a valid panel`)
    }
  } else if (Array.isArray(payload.panel)) {
    for (const panel of payload.panel) {
      await _change(context, payload.type, panel, toggled)
    }
  } else {
    await _change(context, payload.type, payload.panel, toggled)
  }
}

const module: Module<PanelsState, RootState> = {
  namespaced: true,

  state: {
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
      gaussianRandomFields: null,
    },
  },

  actions: {
    populate ({ commit }, panels: PanelsState): void {
      for (const type of Object.keys(panels)) {
        for (const panel of Object.keys(panels[`${type}`])) {
          commit('CHANGE', { type, panel, toggled: panels[`${type}`][`${panel}`] })
        }
      }
    },
    async open (context, payload: Payload): Promise <void> {
      await changePanel(context, payload, true)
    },
    async close (context, payload: Payload): Promise<void> {
      await changePanel(context, payload, false)
    },
    async set (context, payload: FullSpecification): Promise<void> {
      await changePanel(context, payload, payload.toggled)
    },
    async change (context, { type, indices }: { type: Section, indices: number[] }): Promise<void> {
      if (!hasPanel(type)) throw new APSTypeError(`${type} is not a legal panel`)
      const panels = indices.map((index): boolean => PANELS[`${type}`][`${index}`])
      for (const panel of PANELS[`${type}`]) {
        await changePanel(context, { type, panel }, panels.includes(panel))
      }
    },
  },

  mutations: {
    CHANGE (state, { type, panel, toggled }: FullSpecification): void {
      Vue.set(state[`${type}`], panel, toggled)
    }
  },

  getters: {
    selection (state): number[] { return getIndices(state, 'selection') },
    preview (state): number[] { return getIndices(state, 'preview') },
    settings (state): number[] { return getIndices(state, 'settings') },
  },
}

export default module
