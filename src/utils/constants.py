class Constants(object):
    @classmethod
    def constants(cls):
        """
        A method for getting the names of the constants defined in the class / category
        :return: A list of strings with the names of constants defined in the class
        :rtype: List[str]
        """
        return [name for name in dir(cls) if not cls._used_internally(name)]

    @classmethod
    def values(cls):
        """
        Gets the values of the different constants
        :return: A list of the definitions of the different constants
        :rtype: List[str]
        """
        return [cls.__getattribute__(cls(), constant) for constant in cls.constants()]

    @classmethod
    def all(cls):
        """
        Gets a dictionary of the constants where the key is the name of the constant, and the value of the constant
        :return: A key, value pair of constants, and their value
        :rtype: Dict[str, str]
        """
        return {constant: cls.__getattribute__(cls(), constant) for constant in cls.constants()}

    @classmethod
    def __contains__(cls, item):
        return item in cls._standard_return_attribute()

    @classmethod
    def __len__(cls):
        return len(cls.constants())

    @classmethod
    def __getitem__(cls, item):
        return cls.__getattribute__(cls(), item)

    @classmethod
    def _standard_return_attribute(cls):
        return cls.values()

    @staticmethod
    def is_key():
        return False

    @staticmethod
    def is_value():
        return False

    @staticmethod
    def _used_internally(name: str) -> bool:
        if name[0:2] == name[-2:] == '__':
            # These are 'magic' methods in Python, and thus used internally
            return True
        elif name[0] == '_':
            # Private methods
            return True
        elif name in ['constants', 'values', 'all', 'is_key', 'is_value']:
            # These are methods in the base class, that are also used internally, and are therefore not constants
            return True
        else:
            return False

    def __repr__(self):
        return ''.join([self.__name__, ': ', ', '.join(self.constants())])


class Key(Constants):
    @staticmethod
    def is_key():
        return True


class Value(Constants):
    @staticmethod
    def is_value():
        return False


class ModeConstants(Key):
    EXECUTION_MODE = 'execution mode'


class ModeOptions(Value):
    READING_MODE = 'reading'
    EXPERIMENTAL_MODE = 'experimental'


class ProjectConstants(Key):
    PATH_OF_PROJECT_FILE = 'path of project file'
    WORKFLOW_NAME = 'workflow name'
    FACIES_PARAMETER_NAME = 'facies parameter name'
    GAUSSIAN_PARAMETER_NAME = 'gaussian parameter name'
    GRID_MODEL_NAME = 'grid model name'
    ZONES_PARAMETER_NAME = 'zone parameter name'
