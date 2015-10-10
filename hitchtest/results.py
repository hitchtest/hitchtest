from jinja2.environment import Environment
from jinja2 import FileSystemLoader
from hitchtest.hitch_stacktrace import TestPosition
from os import path
import colorama
import json
import sys

TEMPLATE_DIR = path.join(path.dirname(path.realpath(__file__)), "templates")

class Results(object):
    def __init__(self, result_list, failedfast, colorless):
        self.result_list = result_list
        self.failedfast = failedfast
        self.colorless = colorless

    def failures(self):
        return [result for result in self.result_list if result.failure]

    def to_dict(self):
        return {
            'one_test': len(self.result_list) == 1,
            'at_least_one_failure': len(self.failures()) > 0,
            'total': len(self.result_list),
            'total_passes': len(self.result_list) - len(self.failures()),
            'total_failures': len(self.failures()),
            'duration': sum([result.duration for result in self.result_list]),
            'failures': [result.to_dict() for result in self.failures()],
            'failedfast': self.failedfast,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_template(self, template):
        if template is None:
            template = "default.jinja2"
        env = Environment()
        env.loader = FileSystemLoader(TEMPLATE_DIR)
        tmpl = env.get_template(path.basename(template))
        return tmpl.render(
            results=self.to_dict(),
            json=self.to_json(),
            Fore=colorama.Fore if not self.colorless else '',
            Back=colorama.Back if not self.colorless else '',
            Style=colorama.Style if not self.colorless else '',
            TestPosition=TestPosition,
        )
