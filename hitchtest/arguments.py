from hitchtest import utils


class Arguments(object):
    """A null-argument, single argument or group of arguments of a hitch test step."""

    def __init__(self, yaml_args):
        """Create arguments from dict (from yaml)."""
        if yaml_args is None:
            self.is_none = True
            self.single_argument = False
        elif type(yaml_args) is str or type(yaml_args) is int or type(yaml_args) is float or type(yaml_args) is bool:
            self.is_none = False
            self.single_argument = True
            self.argument = yaml_args
        else:
            self.is_none = False
            self.single_argument = False
            self.kwargs = yaml_args

    def pythonized_kwargs(self):
        pythonized_dict = {}
        for key, value in self.kwargs.items():
            pythonized_dict[utils.to_underscore_style(key)] = value
        return pythonized_dict

    def to_dict(self):
        if self.is_none:
            return None
        elif self.single_argument:
            return self.argument
        else:
            return self.kwargs
