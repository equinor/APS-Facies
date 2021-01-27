import Message from '@/utils/domain/messages/base'

export default interface MessageState {
  value: Message | null

  autoDismiss: {
    use: boolean
    wait: number
  }
}
