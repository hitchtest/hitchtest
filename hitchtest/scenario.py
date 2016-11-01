from hitchtest.step import Step

class Scenario(object):
    """The series of steps that make up a hitch test."""

    def __init__(self, yaml_scenario, underscore_case_steps=True):
        self.steps = []

        if yaml_scenario is not None:
            for i, yaml_step in enumerate(yaml_scenario, 1):
                self.steps.append(Step(yaml_step, i, underscore_case_steps=underscore_case_steps))

    def to_dict(self):
        return [step.to_dict() for step in self.steps]
