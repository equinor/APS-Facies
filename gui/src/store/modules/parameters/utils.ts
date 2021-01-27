import rms from '@/api/rms'
import { Selectable } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'
import { ActionContext, Module } from 'vuex'

export function makeSelectionModule (fetch: () => Promise<string>): Module<Selectable, RootState> {
  return {
    namespaced: true,
    state: {
      selected: '',
    },
    actions: {
      async fetch ({ dispatch }: ActionContext<Selectable, RootState>): Promise<void> {
        await dispatch('select', await fetch())
      },
      select ({ commit }: ActionContext<Selectable, RootState>, path: string): void {
        commit('CURRENT', path)
      },
    },
    mutations: {
      CURRENT: (state: Selectable, path: string): void => {
        state.selected = path
      }
    },
  }
}

export function makeToleranceModule (name: string): Module<Selectable<number>, RootState> {
  return {
    namespaced: true,

    state: {
      selected: 0,
    },

    actions: {
      async fetch ({ dispatch }): Promise<void> {
        const { tolerance } = await rms.constants(name, 'tolerance')
        await dispatch('select', tolerance)
      },

      async select ({ commit }, value: number): Promise<void> {
        commit('SET', value)
      }
    },

    mutations: {
      SET (state, value: number): void {
        state.selected = value
      },
    },
  }
}
