from step import Step

class Scenario(object):
    def __init__(self, yaml_scenario):
        self.steps = []

        for yaml_step in yaml_scenario:
            self.steps.append(Step(yaml_step))
