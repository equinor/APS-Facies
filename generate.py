from aps.algorithms.defineTruncationRule import DefineTruncationRule

rules = DefineTruncationRule(show_title=True)

rules.readFile('/Users/snis/Projects/APS/GUI/examples/truncation_settings.dat')
rules.createAllCubicPlots()
