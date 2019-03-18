import { Facies, GlobalFacies } from '@/utils/domain'
import Polygon from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'
import { ID } from '@/utils/domain/types'
import { getId } from '@/utils/helpers'

// @ts-ignore
const promiseSimpleCommit = (commit, commitment, data, check = true, error = '') => {
  return new Promise((resolve, reject) => {
    if (check) {
      commit(commitment, data)
      resolve(data)
    } else {
      reject(error)
    }
  })
}

// @ts-ignore
function compareFacies (facies, other, beStrict = false): boolean {
  let equal = facies.name === other.name && facies.code === other.code
  if (beStrict) {
    equal = equal && facies.color === other.color
  }
  return equal
}

// @ts-ignore
function indexOfFacies (state, facies): number { return state.available.findIndex(item => compareFacies(item, facies)) }

// @ts-ignore
const selectOnlyParameter = async ({ dispatch }, result) => {
  if (result.length === 1) {
    await dispatch('select', result[0])
  } else if (result.length === 0) {
    await dispatch('select', null)
  }
}

// @ts-ignore
const fetchParameterHelper = async ({ commit, dispatch }, promise) => {
  const result = await promise
  commit('AVAILABLE', result)
  await selectOnlyParameter({ dispatch }, result)
}

// @ts-ignore
const mirrorZoneRegions = store => {
  // @ts-ignore
  store.subscribe(({ type, payload }, state) => {
    if (
      type.startsWith('zones') &&
      state.regions.use &&
      !!state.zones.current
    ) {
      if (type === 'zones/REGIONS') {
        if (payload.zoneId === state.zones.current) {
          store.commit('regions/AVAILABLE', { regions: payload.regions })
        } else {
          // Nothing to be done
        }
      } else if (type === 'zones/CURRENT') {
        store.commit('regions/AVAILABLE', { regions: state.zones.available[`${payload.id}`].regions })
      } else if (type === 'zones/AVAILABLE') {
        // Something to be done?
      } else if (type === 'zones/SELECTED') {
        // Nothing to do.
        // Handled by zone's selected action
      } else if (type === 'zones/REGION_SELECTED') {
        // Nothing to do.
        // Handled by regions's selected action
      } else {
        throw new Error(`Unsupported commit type, ${type}`)
      }
    }
  })
}

// @ts-ignore
function updateFacies (dispatch, rule: TruncationRule<Polygon>, polygon: Polygon, facies: Facies | ID, swap: boolean = true): Promise {
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

// @ts-ignore
function changeFacies ({ state, commit }, facies): void {
// TODO: Update proportion in truncation rule if applicable
  const old = state.available[`${facies.id}`]
  // need this to be be synchronous:
  const _class = state.global ? Facies : GlobalFacies
  commit('UPDATE', new _class({ _id: facies.id, ...old, ...facies }), () => facies.hasOwnProperty('id'))
}

interface OptionState<T> {
  value: T
  legal: T[]
}

// @ts-ignore
function makeOption<T> (def: T, legal: T[]) {
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
      // @ts-ignore
      set: ({ commit, state }, value): void => {
        if (state.legal.includes(value)) {
          commit('SET', value)
        }
      },
    },
    mutations: {
      // @ts-ignore
      SET: (state, value): void => {
        state.value = value
      },
    },
    getters: {},
  }
}

export {
  promiseSimpleCommit,
  indexOfFacies,
  fetchParameterHelper,
  mirrorZoneRegions,
  updateFacies,
  changeFacies,
  compareFacies,
  makeOption,
  selectOnlyParameter,
}
