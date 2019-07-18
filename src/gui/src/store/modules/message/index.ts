import { DEFAULT_TIME_UNTIL_MESSAGE_DISMISSAL } from '@/config'

import MessageState from '@/store/modules/message/typing'
import { RootState } from '@/store/typing'

import BaseMessage from '@/utils/domain/messages/base'
import { Module } from 'vuex'

const module: Module<MessageState, RootState> = {
  namespaced: true,

  state: {
    value: null,
    autoDismiss: {
      use: true,
      wait: DEFAULT_TIME_UNTIL_MESSAGE_DISMISSAL,
    },
  },

  actions: {
    change ({ commit }, value: BaseMessage): void {
      commit('CHANGE', value)
    }
  },

  mutations: {
    CHANGE (state, value): void { state.value = value },
  }
}

export default module
