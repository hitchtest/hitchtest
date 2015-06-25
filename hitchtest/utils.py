from IPython.terminal.embed import InteractiveShellEmbed
import IPython
import inspect
import signal
import sys
import os

def to_underscore_style(text):
    text = text.lower().replace(" ", "_").replace("-", "_")
    return ''.join(x for x in text if x.isalpha() or x.isdigit() or x == "_")

def ipython(message=None, frame=None):
    """Launch into customized IPython with greedy autocompletion and no prompt to exit."""
    config = IPython.Config({
        'InteractiveShell': {'confirm_exit': False, },
        'IPCompleter': {'greedy': True, }
    })
    InteractiveShellEmbed.instance(config=config)(message, local_ns=frame.f_locals, global_ns=frame.f_globals)

def ipython_embed(message=None, functions_above=0):
    frame = inspect.stack()[functions_above + 1][0]
    ipython(message, frame)

def _write(handle, message):
    if os.isatty(handle.fileno()):
        handle.write(message)
    else:
        handle.write(bytes(message, 'utf8'))
    handle.flush()

def log(message):
    """Output to stdout."""
    import sys
    _write(sys.stdout, message)

def warn(message):
    """Output to stderr."""
    import sys
    _write(sys.stderr, message)


def do_exit(signal, frame):
    """Just exit."""
    sys.exit(1)

def trigger_exit():
    """Ignore all signals (e.g. ctrl-C)."""
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGTERM, do_exit)
    signal.signal(signal.SIGHUP, do_exit)
    signal.signal(signal.SIGQUIT, do_exit)
