import { DEFAULT_COLOR_LIBRARY } from '@/config'
import { FaciesColorsState } from '@/store/modules/constants/typing'
import { RootState } from '@/store/typing'
import ColorLibrary from '@/utils/domain/colorLibrary'
import APSError from '@/utils/domain/errors/base'

import { Color, colorLibraries } from '@/utils/domain/facies/helpers/colors'
import { hasOwnProperty, identify } from '@/utils/helpers'
import Vue from 'vue'
import { Module } from 'vuex'

function makeMapping (from: ColorLibrary, to: ColorLibrary): Map<Color, Color> {
  return from.colors
    .reduce((mapping, color, index): Map<Color, Color> => {
      mapping.set(color, to.colors[index % to.colors.length])
      return mapping
    }, new Map())
}

type AvailableState = Record<string, ColorLibrary>

const makeSet = <T, P> (obj: Record<string, T>, prop: string): Set<P> => new Set(Object.values(obj).map(item => item[prop]))

const hasSameValues = (values: string[], other: string[]): boolean => values.every(value => other.includes(value))
const extract = <T>(obj: AvailableState, prop: string, process = (arr: any): T => arr): T[] => Object.values(obj).map(item => process(item[prop]))
function hasDifferentColors (available: AvailableState, other: AvailableState): boolean {
  return (
    !hasSameValues(extract(available, 'name'), extract(other, 'name'))
  )
}

function merge (available: AvailableState, other: AvailableState): AvailableState {
  const existingNames = makeSet(available, 'name')
  other = Object.keys(other)
    .filter(key => !existingNames.has(other[key].name))
    .reduce((items, key) => {
      items[key] = other[key]
      return items
    }, ({} as AvailableState))
  return {
    ...available,
    ...other,
  }
}

const module: Module<FaciesColorsState, RootState> = {
  namespaced: true,

  state: {
    available: {},
    current: '',
  },

  actions: {
    fetch ({ commit }): void {
      const libraries = Object.keys(colorLibraries)
        .map(name => new ColorLibrary({ name, colors: colorLibraries[`${name}`] }))
      commit('AVAILABLE', identify(libraries))

      const defaultLibrary = libraries.find((library): boolean => library.name === DEFAULT_COLOR_LIBRARY)
      if (!defaultLibrary) throw new APSError(`The default color library, ${DEFAULT_COLOR_LIBRARY}, is not defined`)
      commit('CURRENT', defaultLibrary)
    },

    async populate ({ commit, dispatch, state }, { available, current }): Promise<void> {
      const name = hasOwnProperty(available, current)
        ? available[`${current}`].name
        : DEFAULT_COLOR_LIBRARY
      if (Object.values(state.available).length === 0) {
        await dispatch('fetch')
      } else if (hasDifferentColors(state.available, available)) {
        commit('AVAILABLE', merge(state.available, available))
      }
      const library = Object.values(state.available)
        .find(library => library.name === name)
      if (!library) throw new APSError(`The color library called ${name} does not exist`)
      commit('CURRENT', library)
    },

    async set ({ commit, getters, dispatch }, colorLibrary: ColorLibrary): Promise<void> {
      const previous = getters.current

      commit('CURRENT', colorLibrary)
      await dispatch('facies/global/changeColorPallet', makeMapping(previous, colorLibrary), { root: true })
    },
  },

  mutations: {
    AVAILABLE (state, value): void {
      Vue.set(state, 'available', value)
    },

    CURRENT (state, colorLibrary: ColorLibrary): void {
      state.current = colorLibrary.id
    }
  },

  getters: {
    byCode (state, getters): (code: number) => Color {
      return (code: number): Color => {
        const colors = getters.available
        return colors[`${code % colors.length}`]
      }
    },

    available (state, getter): Color[] {
      return getter.current.colors
    },

    current (state): ColorLibrary {
      return state.available[state.current]
    },

    libraries (state): { text: string, value: ColorLibrary }[] {
      return Object.values(state.available)
        .map(library => {
          return {
            text: library.name,
            value: library,
          }
        })
    },
  },
}

export default module
