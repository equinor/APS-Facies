export type MessageType = 'error' | 'info' | 'success' | 'warning' // Same as Vuetify's

export default abstract class BaseMessage {
  public value: string | Error

  protected constructor(message: string | Error) {
    this.value = message
  }

  public abstract get kind(): MessageType
}
