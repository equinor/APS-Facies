import { APSTypeError } from '@/utils/domain/errors'

export default class CodeError extends APSTypeError {
  public constructor(value?: number) {
    super(
      `The code of a discrete item MUST be non-negative${
        value ? ' (it was ' + value + ')' : ''
      }`,
    )
  }
}
