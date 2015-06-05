import utils


class Arguments(object):
    def __init__(self, yaml_args):
        if yaml_args is None:
            self.is_none = True
            self.single_argument = False
        elif type(yaml_args) is str or type(yaml_args) is int or type(yaml_args) is float:
            self.is_none = False
            self.single_argument = True
            self.argument = yaml_args
        else:
            self.is_none = False
            self.single_argument = False
            self.kwargs = yaml_args

    def to_python(self):
        if self.is_none:
            return ""
        else:
            if self.single_argument:
                return "\"{}\"".format(self.argument)
            else:
                return ', '.join(['{}="{}"'.format(utils.to_underscore_style(x[0]), x[1]) for x in self.kwargs.items()])
