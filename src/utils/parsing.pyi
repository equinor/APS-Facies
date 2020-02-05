# -*- coding: utf-8 -*-
from typing import List, Tuple, NewType

MethodName = NewType('MethodName', str)
Arguments = NewType('Arguments', List[str])


def _sanitize_for_json(raw: str) -> str: ...
def _get_arguments(raw: str) -> Arguments: ...
def parse_signature(signature: str) -> Tuple[MethodName, Arguments]: ...
