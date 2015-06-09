from os import path, remove, chdir, makedirs, system
from jinja2.environment import Environment
from jinja2 import FileSystemLoader
from IPython.core import ultratb
from test import Test
import subprocess
import inspect
import jinja2
import yaml
import sys
import imp
import sys
import os


#HITCHTEST_DIR = path.dirname(path.realpath(__file__))

class Module(object):
    def __init__(self, filename, engine_folder, dict_vars):
        self.filename = path.realpath(filename)
        #self.template_code = template_code
        self.engine_folder = engine_folder

        self.name = path.split(self.filename)[1].replace(".yml", "")
        self.title = self.name.replace("_", " ").title()
        self.dirname = path.dirname(self.filename)
        self.compiled_dirname = path.join(self.dirname, ".hitch", "tests")


        if dict_vars is None:
            self.dict_vars = {}
        else:
            self.dict_vars = dict_vars

        env = Environment()
        env.loader = FileSystemLoader(engine_folder)
        tmpl = env.get_template(os.path.basename(filename))
        self.test_yaml_text = tmpl.render(**self.dict_vars)

        self.tests = []
        module_yaml_as_dict = yaml.load(self.test_yaml_text)
        if len(module_yaml_as_dict) == 1:
            self.multiple_tests = False
            self.tests = [Test(module_yaml_as_dict[0], self.title)]
        else:
            self.multiple_tests = True
            for i, test_yaml in enumerate(module_yaml_as_dict, 1):
                self.tests.append(Test(test_yaml, "{} {}".format(self.title, i)))

    def printyaml(self):
        sys.stdout.write(self.test_yaml_text)
        sys.stdout.flush()

    def run(self):
        for test in self.tests:
            module_source = os.path.abspath(os.path.join(self.engine_folder, test.engine.split(":")[0]))
            engine_class_name = test.engine.split(":")[1]
            engine_module = imp.load_source("engine", module_source)
            engine_class = [x for x in inspect.getmembers(engine_module) if x[0] == engine_class_name][0][1]
            engine = engine_class(methodName="setUp")
            engine.preconditions = test.preconditions
            engine.settings = self.dict_vars
            failure = False
            tb_printer=ultratb.VerboseTB()

            sys.stdout.write("RUNNING TEST {}\n".format(test.name))
            sys.stdout.flush()

            try:
                engine.setUp()
            except Exception as e:
                tb_printer()
                sys.stderr.write("Exception occurred in {} ({}) setup.\n".format(test.name, self.filename))
                failure = True

            if not failure:
                for i, step in enumerate(test.scenario.steps, 1):
                    try:
                        if step.arguments.is_none:
                            getattr(engine, step.underscore_case_name())()
                        elif step.arguments.single_argument:
                            getattr(engine, step.underscore_case_name())(step.arguments.argument)
                        else:
                            getattr(engine, step.underscore_case_name())(**step.arguments.pythonized_kwargs())
                    except Exception as e:
                        tb_printer()
                        sys.stderr.write("""Exception occurred in "{}" ({} step {}).\n""".format(test.name, self.filename, i))
                        failure = True
                        break

            try:
                engine.tearDown()
            except Exception as e:
                tb_printer()
                sys.stderr.write("""WARNING: Exception occurred in "{}" ({}) tear down.\n""".format(test.name, self.filename))
                sys.exit(1)

        sys.exit(1 if failure else 0)

    #def compile_to_python(self):
        #template = jinja2.Template(self.template_code)
        #if not path.exists(self.compiled_dirname):
            #makedirs(self.compiled_dirname)
        #chdir(self.compiled_dirname)

        #if self.multiple_tests:
            #makedirs(self.name)
            #system("touch {}/__init__.py".format(self.name))

            #for test in self.tests:
                #test.filename = path.join(self.compiled_dirname, self.name, "test_{}.py".format(test.name))
                #with open(test.filename, "w") as output_handle:
                    #output_handle.write(template.render(test=test, settings=self.dict_vars, engine_folder=self.engine_folder))
        #else:
            #self.test_filename = path.join(self.compiled_dirname, "test_{}.py".format(self.name))
            #with open(self.test_filename, "w") as output_handle:
                #output_handle.write(template.render(test=self.test, settings=self.dict_vars, engine_folder=self.engine_folder))

    #def run_python(self, python):
        #if self.multiple_tests:
            #for test in self.tests:
                #returncode = subprocess.call([python, test.filename])
                #if returncode == 0:
                    #pass #remove(test.filename)
        #else:
            #returncode = subprocess.call([python, self.test_filename])
            #if returncode == 0:
                #pass #remove(self.test_filename)
