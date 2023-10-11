import BaseMessage, { MessageType } from '@/utils/domain/messages/base'

export class ErrorMessage extends BaseMessage {
  public constructor(message: string) {
    super(message)
  }

  public get kind(): MessageType {
    return 'error'
  }
}

export class Message extends BaseMessage {
  public constructor(message: string) {
    super(message)
  }

  public get kind(): MessageType {
    return 'info'
  }
}

export class WarningMessage extends BaseMessage {
  public constructor(message: string) {
    super(message)
  }

  public get kind(): MessageType {
    return 'warning'
  }
}

export class SuccessMessage extends BaseMessage {
  public constructor(message: string) {
    super(message)
  }

  public get kind(): MessageType {
    return 'success'
  }
}
