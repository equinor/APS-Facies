import { OptionState } from '@/store/modules/options/typing'
import { SelectableChoice } from '@/store/modules/parameters/typing/helpers'
import { Context, RootGetters, RootState } from '@/store/typing'
import { getId } from '@/utils'
import { Parent, ParentReference } from '@/utils/domain'
import { Dispatch, Module, Store } from 'vuex'

async function selectOnlyParameter<S, G> ({ dispatch }: Context<S, G>, result: string[]): Promise<void> {
  if (result.length === 1) {
    await dispatch('select', result[0])
  } else if (result.length === 0) {
    await dispatch('select', null)
  }
}

async function fetchParameterHelper<S extends SelectableChoice, G> (context: Context<S, G>): Promise<void> {
  const { commit, dispatch, state } = context
  commit('CURRENT', null)
  await dispatch('refresh')
  await selectOnlyParameter(context, state.available)
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

async function populateState<G, S> ({ dispatch }: Context<G, S>, options: {[_: string]: any}): Promise<void> {
  await Promise.all(
    Object.keys(options)
      .map(option => dispatch(`${option}/populate`, options[`${option}`]))
  )
}

function resolveParentReference<S> ({ rootState }: Context<S, RootGetters>, parent: ParentReference | Parent): Parent {
  const zone = rootState.zones.available[getId(parent.zone)]
  if (!zone) throw new Error(`The zone with reference '${parent.zone}' is missing`)
  const region = zone.regions.find(region => region.id === getId(parent.region)) || null
  return {
    zone,
    region,
  }
}

export {
  fetchParameterHelper,
  makeOption,
  selectOnlyParameter,
  displayMessage,
  populateState,
  resolveParentReference,
}
