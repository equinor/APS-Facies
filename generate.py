# Is not used in plugin, but useful to generate truncation map icons manually.
from aps.algorithms.defineTruncationRule import DefineTruncationRule

rules = DefineTruncationRule(show_title=True)

rules.readFile('examples/truncation_settings.dat')
rules.createAllCubicPlots()
