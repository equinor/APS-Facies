import { acceptHMRUpdate, defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { getMessage } from '@/utils/domain/messages'
import { DEFAULT_TIME_UNTIL_MESSAGE_DISMISSAL } from '@/config'
import type { MessageType } from '@/utils/domain/messages/base'
import type BaseMessage from '@/utils/domain/messages/base'

export const useMessageStore = defineStore('messages', () => {
  const message = ref<BaseMessage | null>(null)

  const autoDismiss = reactive({
    use: true,
    wait: DEFAULT_TIME_UNTIL_MESSAGE_DISMISSAL,
  })

  function $reset() {
    message.value = null
    autoDismiss.use = true
    autoDismiss.wait = DEFAULT_TIME_UNTIL_MESSAGE_DISMISSAL
  }

  function change(text: string, type: MessageType) {
    message.value = getMessage(text, type)
  }

  return { message, autoDismiss, change, $reset }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMessageStore, import.meta.hot))
}
