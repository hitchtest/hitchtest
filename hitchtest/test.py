from hitchtest.hitch_stacktrace import HitchStacktrace, TestPosition
from hitchtest.utils import log, warn
from hitchtest.scenario import Scenario
from hitchtest.result import Result
from hitchtest.environment import verify
from os import path
import inspect
import time
import imp
import re


class Test(object):
    def __init__(self, yaml_test, settings, filename, title):
        self.settings = settings
        self.filename = filename
        self.name = yaml_test.get('name', title)
        self.engine = yaml_test.get('engine', 'engine.py:ExecutionEngine')
        self.description = yaml_test.get('description')
        self.preconditions = yaml_test.get('preconditions', {})
        self.tags = yaml_test.get('tags')
        self.features = yaml_test.get('features')
        self.scenario = Scenario(yaml_test.get('scenario', []))

        if re.compile("^(.*?)\:(.*?)$").match(self.engine) is None:
            raise RuntimeError("ERROR : engine should be of the form 'engine_filename.py:ClassName'")
        else:
            module_source = path.abspath(path.join(self.settings['engine_folder'], self.engine.split(":")[0]))
            if not path.exists(module_source):
                raise RuntimeError("ERROR : engine filename '{}' not found.".format(self.engine.split(':')[0]))

            engine_class_name = self.engine.split(":")[1]
            engine_module = imp.load_source("engine", module_source)
            if len([x for x in inspect.getmembers(engine_module) if x[0] == engine_class_name]) == 0:
                raise RuntimeError("ERROR : Class {} not found in engine.".format(engine_class_name))
            self.engine_class = [x for x in inspect.getmembers(engine_module) if x[0] == engine_class_name][0][1]

        if self.name[0].isdigit():
            raise RuntimeError("ERROR : Test names cannot start with a digit.")
        if "test" in self.name.lower():
            warn("WARNING: The word 'test' should not appear in your test name - it is redundant.\n")

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
        stacktrace = None
        engine = None
        failure = False
        show_hitch_stacktrace = self.settings.get("show_hitch_stacktrace", False)

        try:
            engine = self.engine_class(self.settings, self.preconditions)
            engine.name = self.name
            engine.aborted = False
            engine.stacktrace = None
            engine._test = self
        except Exception as e:
            stacktrace = HitchStacktrace(self, TestPosition.SETUP, show_hitch_stacktrace)
            failure = True

        if not failure:
            log("RUNNING TEST {}\n".format(self.name))

            try:
                verify(self.settings.get("environment", []))
                engine.set_up()
            except Exception as e:
                stacktrace = HitchStacktrace(self, TestPosition.SETUP, show_hitch_stacktrace)
                failure = True

            if not failure:
                for step in self.scenario.steps:
                    try:
                        step.run(engine)
                    except Exception as e:
                        stacktrace = HitchStacktrace(self, TestPosition.STEP, show_hitch_stacktrace, step=step)
                        failure = True
                        break

            if not engine.aborted:
                if failure:
                    try:
                        engine.stacktrace = stacktrace
                        engine.on_failure()
                    except Exception as e:
                        stacktrace = HitchStacktrace(self, TestPosition.ON_FAILURE, show_hitch_stacktrace)
                else:
                    try:
                        engine.on_success()
                    except Exception as e:
                        failure = True
                        stacktrace = HitchStacktrace(self, TestPosition.ON_SUCCESS, show_hitch_stacktrace)

            try:
                engine.tear_down()
            except Exception as e:
                failure = True
                stacktrace = HitchStacktrace(self, TestPosition.TEARDOWN, show_hitch_stacktrace)

        duration = time.time() - start_time
        dict_stacktrace = stacktrace.to_dict() if stacktrace is not None else None
        aborted = engine.aborted if engine is not None else False
        result = Result(self, failure, duration, stacktrace=dict_stacktrace, aborted=aborted)
        return result
