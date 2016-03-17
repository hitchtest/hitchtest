from IPython.terminal.embed import InteractiveShellEmbed
from traitlets.config.loader import Config
import functools
import patoolib
import IPython
import inspect
import signal
import shutil
import psutil
import os
import io


def _write(handle, message):
    if isinstance(handle, io.TextIOWrapper):
        handle.write(message)
    else:
        handle.write(message.encode('utf8'))
    handle.flush()

def log(message):
    """Output to stdout."""
    import sys
    _write(sys.stdout, message)

def warn(message):
    """Output to stderr."""
    import sys
    _write(sys.stderr, message)

def to_underscore_style(text):
    """Changes "Something like this" to "something_like_this"."""
    text = text.lower().replace(" ", "_").replace("-", "_")
    return ''.join(x for x in text if x.isalpha() or x.isdigit() or x == "_")

def ipython(message=None, frame=None):
    """Launch into customized IPython with greedy autocompletion and no prompt to exit.
       If stdin is not tty, just issue warning message."""
    import sys
    if os.isatty(sys.stdin.fileno()):
        config = Config({
            'InteractiveShell': {'confirm_exit': False, },
            'IPCompleter': {'greedy': True, }
        })
        InteractiveShellEmbed.instance(config=config)(message, local_ns=frame.f_locals, global_ns=frame.f_globals)
    else:
        warn("==========> IPython cannot be launched if stdin is not a tty.\n\n")

def ipython_embed(message=None, functions_above=0):
    frame = inspect.stack()[functions_above + 1][0]
    ipython(message, frame)

def stop_ipython():
    from IPython.terminal.interactiveshell import TerminalInteractiveShell
    TerminalInteractiveShell.exit_now = True

def do_exit(signal, frame):
    """Just exit."""
    import sys
    sys.exit(1)

def signals_trigger_exit():
    """Make all signals cause a system exit."""
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGTERM, do_exit)
    signal.signal(signal.SIGHUP, do_exit)
    signal.signal(signal.SIGQUIT, do_exit)

def ignore_signals():
    """Ignore all signals (e.g. ctrl-C)."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGQUIT, signal.SIG_IGN)

def signal_pass_on_to_separate_process_group(pid):
    def pass_on_signal(pid, signum, frame):
        os.kill(pid, signum)

    signal.signal(signal.SIGINT, functools.partial(pass_on_signal, pid))
    signal.signal(signal.SIGTERM, functools.partial(pass_on_signal, pid))
    signal.signal(signal.SIGHUP, functools.partial(pass_on_signal, pid))
    signal.signal(signal.SIGQUIT, functools.partial(pass_on_signal, pid))

def extract_archive(filename, directory):
    patoolib.extract_archive(filename, outdir=directory)


class DownloadError(Exception):
    pass


def download_file(downloaded_file_name, url, max_connections=2, max_concurrent=5):
    """Download file to specified location."""
    from commandlib import Command, CommandError, run
    if os.path.exists(downloaded_file_name):
        return

    log("Downloading: {}\n".format(url))
    aria2c = Command("aria2c")
    aria2c = aria2c("--max-connection-per-server={}".format(max_connections))
    aria2c = aria2c("--max-concurrent-downloads={}".format(max_concurrent))

    try:
        if os.path.isabs(downloaded_file_name):
            run(aria2c("--dir=/", "--out={}.part".format(downloaded_file_name), url))
        else:
            run(aria2c("--dir=.", "--out={}.part".format(downloaded_file_name), url))
    except CommandError:
        raise DownloadError("Failed to download {}. Re-running may fix the problem.".format(url))

    shutil.move(downloaded_file_name + ".part", downloaded_file_name)


def get_hitch_directory():
    """Get the hitch directory by working backwards from the virtualenv python."""
    import sys
    return os.path.abspath(
        os.path.join(os.path.dirname(sys.executable), "..", "..")
    )
