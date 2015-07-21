class Result(object):
    def __init__(self, test, failure, duration, stacktrace=None, aborted=False, test_out=None, test_err=None):
        self.test = test.to_dict()
        self.failure = failure
        self.duration = duration
        self.stacktrace = stacktrace
        self.aborted = aborted
        self.test_out = test_out
        self.test_err = test_err

    def to_dict(self):
        return {
            'test': self.test,
            'failure': self.failure,
            'duration': self.duration,
            'stacktrace': self.stacktrace,
        }
