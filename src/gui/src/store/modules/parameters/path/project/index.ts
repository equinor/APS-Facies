import rms from '@/api/rms'
import ProjectPathState from '@/store/modules/parameters/path/project/typing'
import { RootState } from '@/store/typing'
import { ActionContext } from 'vuex'

export default {
  namespaced: true,
  state: {
    selected: '',
  },
  actions: {
    async fetch ({ dispatch }: ActionContext<ProjectPathState, RootState>): Promise<void> {
      const path = await rms.projectDirectory()
      await dispatch('select', path)
    },
    select ({ commit }: ActionContext<ProjectPathState, RootState>, path: string): void {
      commit('CURRENT', path)
    },
  },
  mutations: {
    CURRENT: (state: ProjectPathState, path: string): void => {
      state.selected = path
    }
  },
}
