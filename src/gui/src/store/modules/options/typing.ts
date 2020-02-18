export interface OptionState<T> {
  value: T
  legal: T[]
}

export default interface OptionsState {
  showNameOrNumber: {
    zone: OptionState<string>
    region: OptionState<string>
  }
  automaticAlphaFieldSelection: OptionState<boolean>
  automaticObservedFaciesSelection: OptionState<boolean>
  filterZeroProbability: OptionState<boolean>
  automaticFaciesFill: OptionState<boolean>
  automaticFaciesSelection: OptionState<boolean>
  runFmuWorkflows: OptionState<boolean>
  importFields: OptionState<boolean>
  colorScale: OptionState<string>
}
