import inspect
import signal
from hitchtest import utils
from hitchtest.signal_manager import SignalManager

class HitchAbortedException(Exception):
    pass

class ExecutionEngine(object):
    def __init__(self, settings, preconditions):
        self.settings = settings
        self.preconditions = preconditions
        self.signal_manager = SignalManager(self.abort)

    def set_up(self):
        pass

    def on_success(self):
        pass

    def on_failure(self):
        pass

    def tear_down(self):
        pass

    def ipython(self, message):
        self.signal_manager.turn_off_signal_handler(signal.SIGINT)
        utils.ipython_embed(message)
        self.signal_manager.attach_handler(signal.SIGINT, self.abort)

    def abort(self, signal, frame):
        self.aborted = True
        utils.stop_ipython()
        raise HitchAbortedException("Hitch aborted")
