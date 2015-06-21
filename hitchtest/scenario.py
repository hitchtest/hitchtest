from hitchtest.step import Step

class Scenario(object):
    def __init__(self, yaml_scenario):
        self.steps = []

        for i, yaml_step in enumerate(yaml_scenario, 1):
            self.steps.append(Step(yaml_step, i))

    def to_dict(self):
        return [step.to_dict() for step in self.steps]
