class Result(object):
    def __init__(self, test, failure, duration, stacktrace=None, test_out=None, test_err=None):
        self.test = test
        self.failure = failure
        self.duration = duration
        self.stacktrace = stacktrace
        self.test_out = test_out
        self.test_err = test_err

    def to_dict(self):
        return {
            'test': self.test.to_dict(),
            'failure': self.failure,
            'duration': self.duration,
            'stacktrace': self.stacktrace,
        }
