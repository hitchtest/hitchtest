from os import path, remove, chdir, makedirs, system
from test import Test
import subprocess
import jinja2
import yaml
import sys

HITCHTEST_DIR = path.dirname(path.realpath(__file__))

class Module(object):
    def __init__(self, filename, engine_folder, template_code, dict_vars):
        self.filename = path.realpath(filename)
        self.template_code = template_code
        self.engine_folder = engine_folder

        self.name = path.split(self.filename)[1].replace(".yml", "")
        self.title = self.name.replace("_", " ").title()
        self.dirname = path.dirname(self.filename)
        self.compiled_dirname = path.join(self.dirname, ".hitch", "tests")


        if dict_vars is None:
            self.dict_vars = {}
        else:
            self.dict_vars = dict_vars

        with open(filename) as test_handle:
            test_yaml_text = jinja2.Template(test_handle.read()).render(**self.dict_vars)

        self.tests = []
        module_yaml_as_dict = yaml.load(test_yaml_text)
        if len(module_yaml_as_dict) == 1:
            self.multiple_tests = False
            self.test = Test(module_yaml_as_dict[0], self.title)
        else:
            self.multiple_tests = True
            for i, test_yaml in enumerate(module_yaml_as_dict, 1):
                self.tests.append(Test(test_yaml, "{} {}".format(self.title, i)))

    def compile_to_python(self):
        template = jinja2.Template(self.template_code)
        if not path.exists(self.compiled_dirname):
            makedirs(self.compiled_dirname)
        chdir(self.compiled_dirname)

        if self.multiple_tests:
            makedirs(self.name)
            system("touch {}/__init__.py".format(self.name))

            for test in self.tests:
                test.filename = path.join(self.compiled_dirname, self.name, "test_{}.py".format(test.name))
                with open(test.filename, "w") as output_handle:
                    output_handle.write(template.render(test=self.test, VARS=self.dict_vars, engine_folder=self.engine_folder))
        else:
            self.test_filename = path.join(self.compiled_dirname, "test_{}.py".format(self.name))
            with open(self.test_filename, "w") as output_handle:
                output_handle.write(template.render(test=self.test, VARS=self.dict_vars, engine_folder=self.engine_folder))

    def run_python(self, python):
        if self.multiple_tests:
            for test in self.tests:
                returncode = subprocess.call([python, test.filename])
                if returncode == 0:
                    pass #remove(test.filename)
        else:
            returncode = subprocess.call([python, self.test_filename])
            if returncode == 0:
                pass #remove(self.test_filename)
