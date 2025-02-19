#!/bin/env python
# -*- coding: utf-8 -*-
from typing import NewType, Union, Tuple, List, Optional, Dict
from xml.etree.ElementTree import Element, ElementTree

import copy

from aps.utils.constants.simple import Debug
from aps.utils.exceptions.xml import ReadingXmlError
from aps.utils.records import FaciesRecord
from aps.utils.types import FaciesName, FaciesCode


class Facies:
    __slots__ = '_name', '_code'

    def __init__(self, name: FaciesName, code: FaciesCode):
        self._name = name
        self._code = code

    def __eq__(self, other: 'Facies') -> bool:
        return self.name == other.name or self.code == other.code

    def __getitem__(self, item: int) -> Union[int, str]:
        if item == 0:
            return self.name
        elif item == 1:
            return self.code
        else:
            raise IndexError('list index out of range')

    def __repr__(self):
        return 'Facies({name}, {code})'.format(name=self.name, code=self.code)

    @property
    def name(self) -> FaciesName:
        return self._name

    @property
    def code(self) -> FaciesCode:
        return self._code

    @classmethod
    def from_definition(
        cls,
        definition: Union[
            FaciesRecord,
            Tuple[str, int],
            List[Union[str, int]],
        ],
    ) -> 'Facies':
        definition = FaciesRecord._make(definition)
        return cls(
            name=definition.Name,
            code=definition.Code,
        )

    def to_list(self) -> Tuple[FaciesName, FaciesCode]:
        return self.name, self.code


class FaciesTable(list):
    def __init__(self, facies: Optional[List[Facies]] = None):
        super().__init__(facies or [])

    def __getitem__(self, item: Union[int, FaciesName]) -> Facies:
        if isinstance(item, int) or isinstance(item, slice):
            return super().__getitem__(item)
        elif isinstance(item, str):
            for facies in self:
                if item == facies.name:
                    return facies
        raise IndexError('The facies with index/name "{}" does not exist'.format(item))

    def __contains__(self, item: Union[FaciesName, Facies]) -> bool:
        return any(item == facies for facies in self)

    @property
    def names(self) -> List[FaciesName]:
        return [facies.name for facies in self]

    def append(self, facies: Facies) -> None:
        if facies in self:
            raise ValueError('Facies names, and codes MUST be unique')
        super().append(facies)

    def pop(self, facies: Optional[Union[int, FaciesName, Facies]] = None) -> Facies:
        if isinstance(facies, int):
            return super().pop(facies)
        elif isinstance(facies, str):
            for i in range(len(self)):
                if self[i].name == facies:
                    return super().pop(i)
        elif isinstance(facies, Facies):
            self.pop(facies.name)
        raise IndexError('The given index/facies "{}" does not exist'.format(facies))


class APSMainFaciesTable:
    """
    Keeps the global facies table. All facies used in the APS model must exist in this table before being used.

     Public member functions:
       Constructor:  def __init__(self, ET_Tree=None, modelFileName=None, debug_level=Debug.OFF)

       def initialize(self,fTable)
                  - Initialize the object from a facies/code dictionary object

      --- Get functions ---
       def getNFacies(self)
       def getClassName(self)
       def getFaciesTable(self)
       def getFaciesName(self, fIndx)
       def getFaciesCode(self, fIndx)
       def getFaciesCodeForFaciesName(self, fName)
       def getFaciesIndx(self, fName)

       --- Set functions ---
       def add_facies(self, faciesName, code)
       def remove_facies(self, faciesName):

       --- Check functions ---
       def checkWithFaciesTable(self, fName)

       --- Write ---
       def XMLAddElement(self, root)
                - Add data to xml tree

     Private member functions:

       def __checkUniqueFaciesNamesAndCodes(self)
    """

    def __init__(
        self,
        ET_Tree: Optional[ElementTree] = None,
        modelFileName: Optional[str] = None,
        facies_table: Optional[Dict[int, str]] = None,
        blocked_well=None,
        blocked_well_log=None,
        debug_level: Debug = Debug.OFF,
    ) -> None:
        self.__debug_level = debug_level
        self.__class_name = self.__class__.__name__
        self.__model_file_name = modelFileName

        self.__blocked_well = blocked_well
        self.__blocked_well_log = blocked_well_log

        # Input facies_table must be a dictionary
        self.__facies_table = FaciesTable()
        if facies_table is not None:
            for code in facies_table.keys():
                self.__facies_table.append(
                    Facies(name=facies_table.get(code), code=int(code))
                )

        if ET_Tree is not None:
            # Search xml tree for model file to find the specified Main facies table
            self.__interpretXMLTree(ET_Tree)
            if self.__debug_level >= Debug.VERY_VERBOSE:
                print('--- Call APSMainFaciesTable init')

    def __interpretXMLTree(self, ET_Tree: ElementTree) -> None:
        root = ET_Tree.getroot()

        # Read main facies table for the model
        kw = 'MainFaciesTable'
        obj = root.find(kw)
        if obj is None:
            raise ReadingXmlError(model_file_name=self.__model_file_name, keyword=kw)
        else:
            attr_blockedWell = obj.get('blockedWell')
            if attr_blockedWell is None:
                raise ReadingXmlError(
                    model_file_name=self.__model_file_name, keyword=kw
                )
            else:
                self.__blocked_well = attr_blockedWell
            attr_blockedWellLog = obj.get('blockedWellLog')
            if attr_blockedWellLog is None:
                raise ReadingXmlError(
                    model_file_name=self.__model_file_name, keyword=kw
                )
            else:
                self.__blocked_well_log = attr_blockedWellLog
            facies_table = obj
            for facies in facies_table.findall('Facies'):
                self.__facies_table.append(
                    Facies(name=facies.get('name'), code=int(facies.find('Code').text))
                )
            if not self.__facies_table:
                raise ReadingXmlError(
                    keyword='Facies',
                    model_file_name=self.__model_file_name,
                    parent_keyword='MainFaciesTable',
                )
        if not self.__checkUniqueFaciesNamesAndCodes():
            raise ValueError(
                'The facies table has two or more facies with the same code and/or name.'
            )
        return

    def __len__(self) -> int:
        return len(self.__facies_table)

    def getClassName(self) -> str:
        return copy.copy(self.__class_name)

    def getFaciesTable(self) -> FaciesTable:
        return copy.copy(self.__facies_table)

    def getFaciesName(self, index: int) -> FaciesName:
        return self.__facies_table[index].name

    def getFaciesCode(self, index: int) -> FaciesCode:
        return int(self.__facies_table[index].code)

    def getFaciesCodeForFaciesName(self, facies_name: FaciesName) -> int:
        for facies in self.__facies_table:
            if facies.name == facies_name:
                return facies.code
        return -1

    def getFaciesIndx(self, facies_name: FaciesName) -> int:
        for i in range(len(self)):
            facies = self.__facies_table[i]
            name = facies.name
            if facies_name == name:
                return i
        raise ValueError(
            'Can not find facies with name {} in facies table'.format(facies_name)
        )

    def add_facies(self, name: FaciesName, code: FaciesCode) -> None:
        self.__facies_table.append(Facies(name, code))

    def remove_facies(self, facies_name: FaciesName) -> None:
        self.__facies_table.pop(facies_name)

    def __contains__(self, item: Facies) -> bool:
        return item in self.__facies_table

    def has_facies_int_facies_table(self, facies_name: FaciesName) -> bool:
        return facies_name in [facies.name for facies in self.__facies_table]

    def XMLAddElement(self, root: Element) -> None:
        facies_table = Element('MainFaciesTable')
        facies_table.attrib = {
            'blockedWell': self.__blocked_well,
            'blockedWellLog': self.__blocked_well_log,
        }
        root.append(facies_table)
        for facies in self.__facies_table:
            facies_element = Element('Facies', {'name': facies.name})
            facies_table.append(facies_element)
            code = Element('Code')
            code.text = ' ' + str(facies.code) + ' '
            facies_element.append(code)

    def __checkUniqueFaciesNamesAndCodes(self) -> bool:
        for i in range(len(self)):
            f1 = self.__facies_table[i].name
            for j in range(i + 1, len(self)):
                f2 = self.__facies_table[j].name
                if f1 == f2:
                    print('Error: In ' + self.__class_name)
                    print('Error: Facies name: ' + f1 + ' is specified multiple times')
                    return False
        for i in range(len(self)):
            c1 = self.__facies_table[i].code
            for j in range(i + 1, len(self)):
                c2 = self.__facies_table[j].code
                if c1 == c2:
                    print('Error: In ' + self.__class_name)
                    print(
                        'Error: Facies code: '
                        + str(c1)
                        + ' is specified multiple times'
                    )
                    return False
        return True
