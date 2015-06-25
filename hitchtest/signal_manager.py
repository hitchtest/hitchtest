import signal


class SignalManager(object):
    NAMES = dict((getattr(signal, n), n) \
        for n in dir(signal) if n.startswith('SIG') and '_' not in n )

    def __init__(self, abort_handler):
        self._original_signals = {}
        for sig in [signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT, signal.SIGINT]:
            self._save_original_signal_handler(sig)
            self.attach_handler(sig, abort_handler)

    def _save_original_signal_handler(self, sig):
        self._original_signals[sig] = signal.getsignal(sig)

    def turn_off_signal_handler(self, sig):
        if sig in self._original_signals:
            signal.signal(sig, self._original_signals[sig])
        else:
            raise RuntimeError("Signal {} not in original signals.".format(sig))

    def attach_handler(self, sig, handler):
        signal.signal(sig, handler)
