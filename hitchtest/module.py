from os import path, remove, chdir, makedirs, system
from jinja2.environment import Environment
from jinja2 import FileSystemLoader
from hitchtest.test import Test
import subprocess
import inspect
import jinja2
import yaml
import time
import sys
import imp
import sys
import os


class Module(object):
    def __init__(self, filename, settings):
        self.filename = path.realpath(filename)
        self.engine_folder = settings['engine_folder']

        self.name = path.split(self.filename)[1].replace(".test", "")
        self.title = self.name.replace("_", " ").title()
        self.dirname = path.dirname(self.filename)


        if settings is None:
            self.settings = {}
        else:
            self.settings = settings

        env = Environment()
        env.loader = FileSystemLoader(self.engine_folder)
        tmpl = env.get_template(filename)
        self.test_yaml_text = tmpl.render(**self.settings)

        self.tests = []
        module_yaml_as_dict = yaml.load(self.test_yaml_text)

        if len(module_yaml_as_dict) == 1:
            self.multiple_tests = False
            self.tests = [Test(module_yaml_as_dict[0], self.settings, self.filename, self.title)]
        else:
            self.multiple_tests = True
            for i, test_yaml in enumerate(module_yaml_as_dict, 1):
                self.tests.append(
                    Test(test_yaml, self.settings, self.filename, "{} {}".format(self.title, i))
                )
