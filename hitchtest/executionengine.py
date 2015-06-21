
class ExecutionEngine(object):
    def __init__(self, settings, preconditions):
        self.settings = settings
        self.preconditions = preconditions

    def set_up(self):
        pass

    def on_success(self):
        pass

    def on_failure(self):
        pass

    def tear_down(self):
        pass
