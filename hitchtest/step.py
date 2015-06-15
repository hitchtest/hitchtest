from arguments import Arguments
import utils


class Step(object):
    def __init__(self, yaml_step, index):
        self.index = int(index)
        if type(yaml_step) is str:
            self.name = str(yaml_step)
            self.arguments = Arguments(None)
        elif type(yaml_step) is dict and len(yaml_step.keys()) == 1:
            self.name = yaml_step.keys()[0]
            self.arguments = Arguments(yaml_step.values()[0])
        else:
            raise RuntimeError("Invalid YAML in step '{}'".format(yaml_step))

    def __str__(self):
        return self.name

    def underscore_case_name(self):
        return utils.to_underscore_style(self.name)

    def to_dict(self):
        return {'index': self.index, 'name': self.name, 'arguments': self.arguments.to_dict(), }

    def run(self, engine):
        if self.arguments.is_none:
            getattr(engine, self.underscore_case_name())()
        elif self.arguments.single_argument:
            getattr(engine, self.underscore_case_name())(self.arguments.argument)
        else:
            getattr(engine, self.underscore_case_name())(**self.arguments.pythonized_kwargs())
