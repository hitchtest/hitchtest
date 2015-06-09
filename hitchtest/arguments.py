import utils


class Arguments(object):
    """A group of arguments of a hitch test step."""

    def __init__(self, yaml_args):
        """Create arguments from dict (from yaml)."""
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

    def pythonized_kwargs(self):
        pythonized_dict = {}
        for key, value in self.kwargs.items():
            pythonized_dict[utils.to_underscore_style(key)] = value
        return pythonized_dict

    #def to_python(self):
        #"""Create python code form arguments."""
        #def pythonize(obj):
            #if type(obj) is str:
                #return "\"{}\"".format(
                    #obj.replace("\n", "\\n").replace("\"", "\\\"")
                #)
            #else:
                #return obj

        #if self.is_none:
            #return ""
        #else:
            #if self.single_argument:
                #return pythonize(self.argument)
            #else:
                #return ', '.join([
                    #'{}={}'.format(
                        #utils.to_underscore_style(x[0]),  # Variable
                        #pythonize(x[1]),                  # Value (newlines escaped if string)
                    #) for x in self.kwargs.items()
                #])
