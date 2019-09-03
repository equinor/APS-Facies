import { DEFAULT_COLOR_LIBRARY } from '@/config'
import { FaciesColorsState } from '@/store/modules/constants/typing'
import { RootState } from '@/store/typing'
import ColorLibrary from '@/utils/domain/colorLibrary'
import APSError from '@/utils/domain/errors/base'

import { Color, colorLibraries } from '@/utils/domain/facies/helpers/colors'
import { identify } from '@/utils/helpers'
import Vue from 'vue'
import { Module } from 'vuex'

function makeMapping (from: ColorLibrary, to: ColorLibrary): Map<Color, Color> {
  return from.colors
    .reduce((mapping, color, index): Map<Color, Color> => {
      mapping.set(color, to.colors[index % to.colors.length])
      return mapping
    }, new Map())
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
      const name = available.hasOwnProperty(current)
        ? available[`${current}`].name
        : DEFAULT_COLOR_LIBRARY
      if (Object.values(state.available).length === 0) {
        await dispatch('fetch')
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
