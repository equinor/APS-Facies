import type { MessageType } from '@/utils/domain/messages/base'
import BaseMessage from '@/utils/domain/messages/base'

export function getMessage(
  message: string,
  type: MessageType,
): ErrorMessage | Message | WarningMessage | SuccessMessage {
  switch (type) {
    case 'error':
      return new ErrorMessage(message)
    case 'info':
      return new Message(message)
    case 'warning':
      return new WarningMessage(message)
    case 'success':
      return new SuccessMessage(message)
  }
}

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
