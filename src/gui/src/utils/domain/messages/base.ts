export type MessageType = 'error' | 'info' | 'success' | 'warning' // Save as Vuetify's

export default abstract class BaseMessage {
  public value: string

  protected constructor (message: string) {
    this.value = message
  }

  public abstract get kind (): MessageType
}
