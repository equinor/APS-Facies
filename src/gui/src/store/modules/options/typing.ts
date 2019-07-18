export interface OptionState<T> {
  value: T
  legal: T[]
}

export default interface OptionsState {
  showNameOrNumber: OptionState<string>
  automaticAlphaFieldSelection: OptionState<boolean>
  filterZeroProbability: OptionState<boolean>
  automaticFaciesFill: OptionState<boolean>
  automaticFaciesSelection: OptionState<boolean>
}
