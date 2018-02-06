class Constants(object):
    def __init__(self, constant=None):
        self.constant = None
        if constant in self.constants() or constant is None:
            self.constant = constant
        else:
            raise ValueError(
                "The given constant, {constant} is not valid for {class_name}"
                "".format(constant=constant, class_name=self.__class__.__name__)
            )

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            pass

    def get_value(self):
        pass

    def get_constant(self):
        pass

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.get_value() == other.get_value() and self.get_constant() == other.get_constant()
        return False

    @classmethod
    def constants(cls, local: bool = False, sort: bool = False):
        """
         A method for getting the names of the constants defined in the class / category.
        :param local: A flag for getting the constants that are ONLY defined in the particular class, and NOT in in any
                      of its parents. Default is to give ALL constants.
        :type local: bool
        :param sort: A flag for having the constants sorted alphabetically.
        :type sort: bool
        :return: A (sorted) list of strings with the names of constants (only) defined in the class.
        :rtype: List[str]
        """
        all_constants = [name for name in dir(cls) if not cls._used_internally(name)]
        if local and hasattr(cls.__base__, 'constants'):
            irrelevant_constants = set(cls.__base__.constants())
            all_constants = [constant for constant in all_constants if constant not in irrelevant_constants]
        if sort:
            all_constants.sort()
        return all_constants

    @classmethod
    def values(cls, local: bool = False, sort: bool = False):
        """
        Gets the values of the different constants.
        :param local: A flag for getting the constants that are ONLY defined in the particular class, and NOT in in any
                      of its parents. Default is to give ALL constants.
        :type local: bool
        :param sort: A flag for having the constants sorted alphabetically.
        :type sort: bool
        :return: A list of the definitions of the different constants
        :rtype: List[ValueType]
        """
        return [cls.__getattribute__(cls(), constant) for constant in cls.constants(local=local, sort=sort)]

    @classmethod
    def all(cls, local: bool = False):
        """
        Gets a dictionary of the constants where the key is the name of the constant, and the value of the constant
        :param local: A flag for getting the constants that are ONLY defined in the particular class, and NOT in in any
                      of its parents. Default is to give ALL constants.
        :type local: bool
        :return: A key, value pair of constants, and their value
        :rtype: Dict[str, ValueTypes]
        """
        return {constant: cls.__getattribute__(cls(), constant) for constant in cls.constants(local=local)}

    @classmethod
    def __contains__(cls, item) -> bool:
        return item in cls._standard_return_attribute()

    @classmethod
    def __iter__(cls):
        return cls.all().__iter__()

    @classmethod
    def __len__(cls) -> int:
        return len(cls.constants())

    @classmethod
    def __getitem__(cls, item: str):
        return cls.__getattribute__(cls(), item)

    @classmethod
    def _standard_return_attribute(cls):
        return cls.values()

    @staticmethod
    def is_key() -> bool:
        return False

    @staticmethod
    def is_value() -> bool:
        return False

    @staticmethod
    def is_icon() -> bool:
        return False

    @staticmethod
    def _used_internally(name: str) -> bool:
        # FIXME: Return true iff name is all uppercase?
        if (
                name[0:2] == name[-2:] == '__'  # These are 'magic' methods in Python, and thus used internally
                or name[0] == '_'  # Private methods
                or name.islower()
                # These are methods in the base class, that are also used internally, and are therefore not constants
        ):
            return True
        else:
            return False

    @classmethod
    def __repr__(cls):
        return ''.join([cls.__name__, ': ', ', '.join(cls.constants())])


class Key(Constants):
    @staticmethod
    def is_key():
        return True


class Value(Constants):
    @staticmethod
    def is_value():
        return False


class Icon(Constants):
    @staticmethod
    def is_icon():
        return True
