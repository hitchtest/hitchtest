from arguments import Arguments
import utils


class Step(object):
    def __init__(self, yaml_step):
        if type(yaml_step) is str:
            self.name = yaml_step
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
