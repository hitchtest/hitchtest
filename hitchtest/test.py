from hitchtest.hitch_stacktrace import HitchStacktrace, TestPosition
from hitchtest.scenario import Scenario
from hitchtest.result import Result
from hitchtest import utils
from os import path
import inspect
import time
import sys
import imp
import os


class Test(object):
    def __init__(self, yaml_test, settings, filename, title):
        self.settings = settings
        self.filename = filename
        self.name = yaml_test['name'] if 'name' in yaml_test else title
        self.engine = yaml_test['engine']
        self.description = yaml_test['description'] if 'description' in yaml_test else None
        self.preconditions = yaml_test['preconditions'] if 'preconditions' in yaml_test else None
        self.tags = yaml_test['tags'] if 'tags' in yaml_test else None
        self.features = yaml_test['features'] if 'features' in yaml_test else None
        self.scenario = Scenario(yaml_test['scenario'])

        if "test" in self.name.lower():
            sys.stderr.write("WARNING: The word 'test' should not appear in your test name - it is redundant.\n")
        if self.name[0].isdigit():
            raise RuntimeError("ERROR : Test names cannot start with a digit.")

    def to_dict(self):
        return {
            "filename": self.filename,
            "name": self.name,
            "engine": self.engine,
            "preconditions": self.preconditions,
            "description": self.description,
            "tags": self.tags,
            "features": self.features,
            "scenario": self.scenario.to_dict(),
        }

    def run(self):
        start_time = time.time()

        module_source = path.abspath(path.join(self.settings['engine_folder'], self.engine.split(":")[0]))
        engine_class_name = self.engine.split(":")[1]
        engine_module = imp.load_source("engine", module_source)
        engine_class = [x for x in inspect.getmembers(engine_module) if x[0] == engine_class_name][0][1]
        engine = engine_class(self.settings, self.preconditions)
        engine.name = self.name
        engine._test = self
        failure = False

        sys.stdout.write("RUNNING TEST {}\n".format(self.name))
        sys.stdout.flush()
        stacktrace = None

        try:
            engine.set_up()
        except Exception as e:
            stacktrace = HitchStacktrace(self, TestPosition.SETUP)
            failure = True

        if not failure:
            for step in self.scenario.steps:
                try:
                    step.run(engine)
                except Exception as e:
                    stacktrace = HitchStacktrace(self, TestPosition.STEP, step=step)
                    failure = True
                    break

        if failure:
            if hasattr(engine, "on_failure"):
                try:
                    engine.on_failure(stacktrace)
                except Exception as e:
                    stacktrace = HitchStacktrace(self, TestPosition.ON_FAILURE)
        else:
            if hasattr(engine, "on_success"):
                try:
                    engine.on_success()
                except Exception as e:
                    stacktrace = HitchStacktrace(self, TestPosition.ON_SUCCESS)

        try:
            engine.tear_down()
        except Exception as e:
            stacktrace = HitchStacktrace(self, TestPosition.TEARDOWN)

        duration = time.time() - start_time
        return Result(self, failure, duration, stacktrace=stacktrace.to_dict() if stacktrace else None)
