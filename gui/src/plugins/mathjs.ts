import { create, all, MathJsStatic } from 'mathjs'

const math = create(all, { number: 'BigNumber' }) as MathJsStatic

export default math
