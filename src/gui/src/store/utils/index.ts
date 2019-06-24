import { Facies } from '@/utils/domain'
import Polygon, { PolygonSerialization } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'
import { ID } from '@/utils/domain/types'
import { getId } from '@/utils/helpers'
import { RootState } from '@/store/typing'
import { Commit, Dispatch, Module } from 'vuex'

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

function updateFacies<P extends Polygon, S extends PolygonSerialization> (
  dispatch: Dispatch,
  rule: TruncationRule<P, S>,
  polygon: Polygon,
  facies: Facies | ID,
  swap: boolean = true
): Promise<void> {
  const existing = rule.polygons
    .find((polygon): boolean => getId(polygon.facies) === getId(facies))
  return existing && swap
    ? dispatch('truncationRules/swapFacies', {
      rule,
      polygons: [polygon, existing]
    })
    : dispatch('truncationRules/updateFacies', {
      rule,
      polygon,
      facies,
    })
}

interface OptionState<T> {
  value: T
  legal: T[]
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
    },
    mutations: {
      SET: (state, value): void => {
        state.value = value
      },
    },
    getters: {},
  }
}

export {
  fetchParameterHelper,
  updateFacies,
  makeOption,
  selectOnlyParameter,
}
