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
