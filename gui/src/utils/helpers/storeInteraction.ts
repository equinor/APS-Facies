import store from '@/store'

import { displayMessage as baseDisplayMessage } from '@/store/utils'

export async function displayMessage (message: string, type = 'info'): Promise<void> {
  await baseDisplayMessage(store, message, type)
}

export async function displayError (message: string): Promise<void> {
  await displayMessage(message, 'error')
}

export async function displayWarning (message: string): Promise<void> {
  await displayMessage(message, 'warning')
}

export async function displaySuccess (message: string): Promise<void> {
  await displayMessage(message, 'success')
}
