import { Zone, Region } from '@/utils/domain'

export default interface CopyPasteState {
  source: Zone | Region | null
  _pasting: {
    [parentId: string]: boolean
  }
}
