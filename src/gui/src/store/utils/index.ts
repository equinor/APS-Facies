import { OptionState } from '@/store/modules/options/typing'
import { RootState } from '@/store/typing'
import { Commit, Dispatch, Module, Store } from 'vuex'

async function selectOnlyParameter ({ dispatch }: { dispatch: Dispatch }, result: string[]): Promise<void> {
  if (result.length === 1) {
    await dispatch('select', result[0])
  } else if (result.length === 0) {
    await dispatch('select', null)
  }
}

async function fetchParameterHelper ({ commit, dispatch }: { commit: Commit, dispatch: Dispatch }, promise: Promise<any>): Promise<void> {
  const result = await promise
  commit('AVAILABLE', result)
  await selectOnlyParameter({ dispatch }, result)
}

function makeOption<T> (def: T, legal: T[]): Module<OptionState<T>, RootState> {
  if (!Array.isArray(legal)) {
    throw new Error('The legal values MUST be a list')
  } else if (legal.indexOf(def) === -1) {
    throw new Error('The default value MUST be a legal value')
  }
  return {
    namespaced: true,
    state: (): OptionState<T> => {
      return {
        value: def,
        legal: legal
      }
    },
    actions: {
      set: ({ commit, state }, value): void => {
        if (state.legal.includes(value)) {
          commit('SET', value)
        }
      },

      populate: async ({ dispatch }, { value }): Promise<void> => {
        await dispatch('set', value)
      },
    },
    mutations: {
      SET: (state, value): void => {
        state.value = value
      },
    },
    getters: {},
  }
}

async function displayMessage (
  context: Store<RootState> | { dispatch: Dispatch },
  message: string,
  type: string,
): Promise<void> {
  const action = 'message/change'
  const payload = { message, type }

  if (context instanceof Store) {
    await context.dispatch(action, payload)
  } else {
    await context.dispatch(action, payload, { root: true })
  }
}

export {
  fetchParameterHelper,
  makeOption,
  selectOnlyParameter,
  displayMessage,
}
