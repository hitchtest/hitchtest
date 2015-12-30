from os import path, remove, chdir, makedirs, system
from jinja2.environment import Environment
from jinja2 import FileSystemLoader, exceptions
from pykwalify.errors import PyKwalifyException
from pykwalify.core import Core
from hitchtest.utils import warn
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


HITCHSCHEMA = path.join(path.dirname(path.realpath(__file__)), "schema.yaml")

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

        with open(filename, "r") as file_handle:
            if file_handle.read() == "":
                warn("{0} is an empty file.\n".format(filename))
                sys.exit(1)

        env = Environment()
        env.loader = FileSystemLoader(path.split(filename)[0])
        try:
            template = env.get_template(path.split(filename)[1])
        except exceptions.TemplateError as error:
            warn("Jinja2 template error in '{}' on line {}:\n==> {}\n".format(
                error.filename, error.lineno, str(error)
            ))
            sys.exit(1)
        self.test_yaml_text = template.render(**self.settings.as_dict())

        if self.test_yaml_text == "":
            warn((
                "{0} rendered as an empty file. "
                "There is probably a problem with your jinja2 template.\n"
            ).format(filename))
            sys.exit(1)

        self.tests = []
        try:
            module_yaml_as_dict = yaml.load(self.test_yaml_text)
        except yaml.parser.MarkedYAMLError as error:
            warn("YAML parser error in {}:\n".format(filename))
            warn(str(error))
            warn("\n")
            sys.exit(1)

        try:
            core = Core(source_data=module_yaml_as_dict, schema_files=[HITCHSCHEMA])
            core.validate(raise_exception=True)
        except PyKwalifyException as error:
            warn("YAML validation error in {}:\n==> {}\n".format(filename, error.msg))
            sys.exit(1)

        if len(module_yaml_as_dict) == 1:
            self.multiple_tests = False
            self.tests = [Test(module_yaml_as_dict[0], self.settings, self.filename, self.title)]
        else:
            self.multiple_tests = True
            for i, test_yaml in enumerate(module_yaml_as_dict, 1):
                self.tests.append(
                    Test(test_yaml, self.settings, self.filename, "{} {}".format(self.title, i))
                )
