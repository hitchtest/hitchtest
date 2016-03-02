import inspect
import signal
from hitchtest import utils
from hitchtest.signal_manager import SignalManager
from path import Path


class HitchAbortedException(Exception):
    pass


class HitchPathError(Exception):
    pass


#class HitchStatePath(Path):
    #def snapshot(path, name=None):
        ##self.abspath()
    
    #def restore(path, name=None):
        ##self.abspath()


class Paths(object):
    def __init__(self):
        self.hitch = Path(utils.get_hitch_directory())
        self.engine = self.hitch.parent
        self.state = self.hitch.joinpath("s")
        
        if not self.state.exists():
            self.state.mkdir()
        
    def __setattr__(self, name, value):
        if not isinstance(value, Path):
            raise HitchPathError("Path '{}' must be of type pathlib.Path".format(value))
        self.__dict__[name] = value


class ExecutionEngine(object):
    def __init__(self, settings, preconditions):
        self.settings = settings
        self.preconditions = preconditions
        self.signal_manager = SignalManager(self.abort)
        self.path = Paths()

    def set_up(self):
        pass

    def on_success(self):
        pass

    def on_failure(self):
        pass

    def tear_down(self):
        pass

    def ipython(self, message=None):
        self.signal_manager.attach_handler(signal.SIGINT, signal.default_int_handler)
        utils.ipython_embed(message)
        self.signal_manager.attach_handler(signal.SIGINT, self.abort)

    def abort(self, signal, frame):
        self.aborted = True
        utils.stop_ipython()
        raise HitchAbortedException
