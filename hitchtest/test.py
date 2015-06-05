import sys
from scenario import Scenario
import utils

class Test(object):
    def __init__(self, yaml_test, title):
        self.name = yaml_test['name'] if 'name' in yaml_test else title
        self.engine = yaml_test['engine']
        self.description = yaml_test['description'] if 'description' in yaml_test else None
        self.preconditions = yaml_test['preconditions'] if 'preconditions' in yaml_test else None
        self.bugs = yaml_test['bugs'] if 'bugs' in yaml_test else None
        self.features = yaml_test['features'] if 'features' in yaml_test else None
        self.scenario = Scenario(yaml_test['scenario'])

        if "test" in self.name.lower():
            sys.stderr.write("WARNING: The word 'test' should not appear in your test name - it is redundant.\n")
        if self.name[0].isdigit():
            raise RuntimeError("ERROR : Test names cannot start with a digit.")

    def engine_import(self):
        return self.engine.split(".")[0]

    def camel_case_name(self):
        return utils.to_camel_case(self.name)

    def underscore_case_name(self):
        return utils.to_underscore_style(self.name)
