from jinja2.environment import Environment
from jinja2 import FileSystemLoader
from os import path
import colorama
import utils
import json
import sys


TEMPLATE_DIR = path.join(path.dirname(path.realpath(__file__)), "templates")

class TestPosition(object):
    SETUP = 1
    TEARDOWN = 2
    ON_FAILURE = 3
    ON_SUCCESS = 4
    STEP = 5

class HitchStacktrace(object):
    """Representation of a python stacktrace."""

    def __init__(self, test, where, step=None):
        """Create this object with sys.exc_info()[2]"""
        self.tracebacks = []
        self.test = test
        self.where = where
        self.step = step
        tb_id = 0
        tb = sys.exc_info()[2]
        self.exception = sys.exc_info()[1]

        # Create list of tracebacks
        while tb is not None:
            filename = tb.tb_frame.f_code.co_filename
            if "hitchtest/" not in filename:
                self.tracebacks.append(HitchTraceback(tb_id, tb))
                tb_id = tb_id + 1
            tb = tb.tb_next

    def to_template(self, template="stacktrace_default.jinja2"):
        env = Environment()
        env.loader = FileSystemLoader(TEMPLATE_DIR)
        tmpl = env.get_template(path.basename(template))
        return tmpl.render(
            stacktrace=self.to_dict(),
            TestPosition=TestPosition,
            json=self.to_json(),
            Fore=colorama.Fore,
            Back=colorama.Back,
            Style=colorama.Style,
        )

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            'test': self.test.to_dict(),
            'step': self.step.to_dict() if self.step else None,
            'where': self.where,
            'tracebacks': [traceback.to_dict() for traceback in self.tracebacks],
            'exception': str(self.exception),
        }

    def __len__(self):
        return len(self.tracebacks)

    def __getitem__(self, index):
        return self.tracebacks[index]



class HitchTraceback(object):
    """Representation of a python traceback caused by a failed test case."""

    def __init__(self, tb_id, traceback):
        self.tb_id = tb_id
        self.traceback = traceback

    def to_dict(self):
        return {
            'id': self.tb_id,
            'filename': self.filename(),
            'lineno': self.lineno(),
            'function': self.func(),
            'line': self.loc(),
            'loc_before': self.loc_before(),
            'loc_after': self.loc_after(),
        }

    def filename(self):
        return self.traceback.tb_frame.f_code.co_filename

    def lineno(self):
        return self.traceback.tb_lineno

    def func(self):
        return self.traceback.tb_frame.f_code.co_name

    def localvars(self):
        return self.traceback.tb_frame.f_locals

    def globalvars(self):
        return self.traceback.tb_frame.f_globals

    def frame(self):
        return self.traceback.tb_frame

    def ipython(self):
        utils.ipython(
            message="Entering {} at line {}".format(self.filename(), self.lineno()),
            frame=self.frame(),
        )

    def loc_before(self):
        with open(self.filename(), 'r') as source_handle:
            contents = source_handle.read().split('\n')
        return contents[self.lineno() - 4:self.lineno() - 2]

    def loc(self):
        with open(self.filename(), 'r') as source_handle:
            contents = source_handle.read().split('\n')
        return contents[self.lineno() - 1]

    def loc_after(self):
        with open(self.filename(), 'r') as source_handle:
            contents = source_handle.read().split('\n')
        return contents[self.lineno():self.lineno() + 2]

    def __repr__(self):
        return "[{}] File {}, line {} in {}: {}".format(
            self.tb_id,
            self.filename(),
            self.lineno(),
            self.func(),
            self.loc()
        )
