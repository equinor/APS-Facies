from pathlib import Path

from typing import Union, Tuple, NewType

FilePath = Union[Path, str]

Number = Union[int, float]

GridSize = Tuple[int, int, int]
SimulationBoxSize = Tuple[float, float, float]
SimulationBoxOrigin = Tuple[float, float]

PropertyName = NewType('PropertyName', str)
XMLKeyword = NewType('XMLKeyword', str)

GaussianFieldName = NewType('GaussianFieldName', str)

FaciesName = NewType('FaciesName', str)
FaciesCode = NewType('FaciesCode', int)
Probability = Union[float, str]

Index = NewType('Index', int)
ErrorCode = NewType('ErrorCode', int)

Point3D = Tuple[float, float, float]
HyperbolicTrendParameters = Tuple[float, float, float, float, float, float]


ModelFile = NewType('ModelFile', str)
ProbabilityLogSpecificationFile = NewType('ProbabilityLogSpecificationFile', str)
OutputModelFile = NewType('OutputModelFile', FilePath)
GlobalVariablesFile = NewType('GlobalVariablesFile', FilePath)
RmsProjectDataFile = NewType('RmsProjectDataFile', FilePath)
TemporaryGaussianSimulation = NewType('TemporaryGaussianSimulation', str)
FmuVariablesFile = NewType('FmuVariablesFile', str)
TaggedVariableFile = NewType('TaggedVariableFile', str)
GridModelName = NewType('GridModelName', str)
BlockedWellSetName = NewType('BlockedWellSetName', str)
FaciesLogName = NewType('FaciesLogName', str)
WorkflowName = NewType('WorkflowName', str)
JobName = NewType('JobName', str)
SeedLogFile = NewType('SeedLogFile', FilePath)


ProjectName = NewType('ProjectName', str)
ProjectPath= NewType('ProjectPath', str)
FmuParameterListPath = NewType('FmuParameterListPath', str)
XML = NewType('XML', str)
TrendName = NewType('TrendName', str)
VariogramName = NewType('VariogramName', str)
GridName = NewType('GridName', str)
DirectionName = NewType('DirectionName', str)
OriginTypeName = NewType('OriginTypeName', str)

ZoneParameter = NewType('ZoneParameter', str)
RegionParameter = NewType('RegionParameter', str)
TrendParameter = NewType('TrendParameter', str)
TrendMapName = NewType('TrendMapName', str)
TrendMapZone = NewType('TrendMapZone', str)
ProbabilityCubeParameter = NewType('ProbabilityCubeParameter', str)
RealizationParameter = NewType('RealizationParameter', str)


ZoneNumber = NewType('ZoneNumber', int)
ZoneName = NewType('ZoneName', str)

RegionNumber = NewType('RegionNumber', int)

Average = NewType('Average', float)
