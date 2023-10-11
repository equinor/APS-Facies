import BaseItem, {
  BaseItemConfiguration,
  BaseItemSerialization,
} from '@/utils/domain/bases/baseItem'
import { Color } from '@/utils/domain/facies/helpers/colors'

export interface ColorLibrarySpecification extends BaseItemConfiguration {
  name: string
  colors: Color[]
}

export interface ColorLibrarySerialization extends BaseItemSerialization {
  name: string
  colors: string[]
}

export default class ColorLibrary extends BaseItem {
  public readonly name: string
  public readonly colors: Color[]

  public constructor({ name, colors, ...rest }: ColorLibrarySpecification) {
    super(rest)
    this.name = name
    this.colors = colors
  }

  public toJSON(): ColorLibrarySerialization {
    return {
      ...super.toJSON(),
      name: this.name,
      colors: this.colors,
    }
  }
}
