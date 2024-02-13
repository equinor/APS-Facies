import { useMessageStore } from '@/stores/messages'
import type { MessageType } from '@/utils/domain/messages/base'

export function displayMessage(message: string, type: MessageType = 'info') {
  const messageStore = useMessageStore()
  messageStore.change(message, type)
}

export function displayError(message: string) {
  displayMessage(message, 'error')
}

export function displayWarning(message: string) {
  displayMessage(message, 'warning')
}

export function displaySuccess(message: string) {
  displayMessage(message, 'success')
}
