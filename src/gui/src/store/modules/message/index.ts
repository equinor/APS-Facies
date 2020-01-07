import { DEFAULT_TIME_UNTIL_MESSAGE_DISMISSAL } from '@/config'

import MessageState from '@/store/modules/message/typing'
import { RootState } from '@/store/typing'
import { ErrorMessage, Message, SuccessMessage, WarningMessage } from '@/utils/domain/messages'

import BaseMessage, { MessageType } from '@/utils/domain/messages/base'
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
    change ({ commit }, value: BaseMessage | { message: string, type: MessageType }): void {
      if (!(value instanceof BaseMessage)) {
        const _class = {
          error: ErrorMessage,
          info: Message,
          warning: WarningMessage,
          success: SuccessMessage,
        }[value.type]
        value = new _class(value.message)
      }
      commit('CHANGE', value)
    }
  },

  mutations: {
    CHANGE (state, value): void { state.value = value },
  }
}

export default module
