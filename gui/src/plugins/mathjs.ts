import { create, all, MathJsStatic } from 'mathjs'

const config = {
  number: 'BigNumber',
}

const math = create(all, config) as MathJsStatic

export default math
