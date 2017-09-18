from src.utils.constants import ProjectConstants, ModeConstants, ModeOptions


class State(dict):
    """
    A class that defines the state of the GUI application.
    """
    def __init__(self, **kwargs):
        super(State, self).__init__(**kwargs)

    def __setattr__(self, key, value):
        # TODO: Make pretty, and robust
        self.__dict__[key] = value

    def __getitem__(self, item):
        # TODO: Make pretty, and robust
        return self.__dict__[item]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        #  TODO: Make pretty, and robust?
        del self.__dict__[key]

    def clear(self):
        # TODO: Should this be allowed?
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def __contains__(self, item):
        return item in self.__dict__

    def update(self, *args, **kwargs):
        # TODO: Should this be allowed?
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __iter__(self):
        return iter(self.__dict__)

    def get_project_data(self):
        return {key: self.__dict__[key] for key in ProjectConstants.values() if key in self.__dict__}

    def set_execution_mode(self, mode):
        if mode not in ModeOptions():
            raise ValueError(
                "The mode '{mode}' is not a valid mode for execution. Please use one of {options}".format(
                    mode=mode,
                    options=', '.join(ModeOptions.values())
                )
            )
        self.__dict__[ModeConstants.EXECUTION_MODE] = mode

    def set_project_path(self, path):
        self.__dict__[ProjectConstants.PATH_OF_PROJECT_FILE] = path
