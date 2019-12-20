# -*- coding: utf-8 -*-
from enum import Enum
from typing import Dict, TypeVar, Optional, Set, List, Type, overload, Tuple, NewType, NamedTuple
from xml.etree.ElementTree import Element

from src.utils.constants.simple import Debug

T = TypeVar('T')
U = TypeVar('U')

ModelFile = NewType('ModelFile', str)
ProbabilityLogSpecificationFile = NewType('ProbabilityLogSpecificationFile', str)
OutputModelFile = NewType('OutputModelFile', str)
GlobalIplFile = NewType('GlobalIplFile', str)
RmsProjectDataFile = NewType('RmsProjectDataFile', str)
TemporaryGaussianSimulation = NewType('TemporaryGaussianSimulation', str)
FmuVariablesFile = NewType('FmuVariablesFile', str)
TaggedVariableFile = NewType('TaggedVariableFile', str)
GridModelName = NewType('GridModelName', str)
BlockedWellSetName = NewType('BlockedWellSetName', str)
FaciesLogName = NewType('FaciesLogName', str)
WorkflowName = NewType('WorkflowName', str)
SeedLogFile = NamedTuple('SeedLogFile', str)


class RunParameters(NamedTuple):
    model_file: ModelFile
    output_model_file: OutputModelFile
    rms_data_file: RmsProjectDataFile
    global_variables_file: GlobalIplFile
    tagged_variables_file: TaggedVariableFile
    tag_all_variables: bool
    fmu_variables_file: FmuVariablesFile
    write_log_file: bool
    seed_log_file: SeedLogFile
    input_directory: TemporaryGaussianSimulation
    probability_log_specification_file: ProbabilityLogSpecificationFile
    facies_code: int
    run_test_script: bool
    debug_level: Debug

    def __getitem__(self, item: str): ...


class SpecificationType(Enum):
    APS_MODEL = 0
    PROBABILITY_LOG = 1
    FACIES_LOG = 2
    CONVERT_BITMAP = 3
    PROBABILITY_TREND = 4


def invert_dict(to_be_inverted: Dict[T, U]) -> Dict[U, T]: ...

@overload
def get_legal_values_of_enum(enum: Enum) -> Set[int]: ...

@overload
def get_legal_values_of_enum(enum: Type[Enum]) -> Set[int]: ...

@overload
def get_printable_legal_values_of_enum(enum: Enum) -> List[str]: ...

@overload
def get_printable_legal_values_of_enum(enum: Type[Enum]) -> List[str]: ...

def get_item_from_model_file(tree: Element, keyword: str, model_file_name: Optional[str]) -> str: ...

def get_selected_zones(tree: Element, keyword: str, model_file: Optional[str]) -> List[int]: ...

@overload
def get_colors(n: int, min_colors: int) -> List[str]: ...

@overload
def get_colors(n: int) -> List[str]: ...

def get_run_parameters(**kwargs) -> RunParameters: ...
def get_model_file_name(
        _default_name: str = 'APS.xml',
        **kwargs
) -> ModelFile: ...
def get_output_model_file(**kwargs) -> OutputModelFile: ...
def get_seed_log_file(**kwargs) -> SeedLogFile: ...
def get_debug_level(**kwargs) -> Debug: ...
def get_global_ipl_file(**kwargs) -> GlobalIplFile: ...
def get_rms_project_data_file(**kwargs) -> RmsProjectDataFile: ...
def _get_value(kwargs: Dict[str, T], legal_kwargs: List[str], default_value: T) -> T: ...
def _get_file_name(kwargs: Dict[str, str], legal_kwargs: List[str], default_name: str) -> str: ...
def get_prefix(**kwargs) -> str: ...
def calc_average(cell_index_defined: List[int], values: List[float]) -> float: ...
def get_workflow_name() -> WorkflowName: ...
def get_specification_file(_type: SpecificationType, **kwargs) -> ProbabilityLogSpecificationFile: ...
