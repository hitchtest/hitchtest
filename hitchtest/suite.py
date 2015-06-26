from os import path, getpgrp, getpgid, tcsetpgrp, fdopen
from hitchtest.utils import log, warn
from hitchtest.results import Results
from hitchtest.result import Result
from functools import partial
import multiprocessing
import psutil
import signal
import termios
import sys
import os


class Suite(object):
    """A group of tests defined at runtime."""
    def __init__(self, test_modules, settings):
        self.test_modules = test_modules
        self.settings = settings

    def tests(self):
        test_list = []
        for test_module in self.test_modules:
            test_list.extend(test_module.tests)
        return test_list

    def printyaml(self):
        """Print the test YAML for jinja2 debugging purposes."""
        for test_module in self.test_modules:
            log("\n# {}\n{}\n".format(
                test_module.filename,
                test_module.test_yaml_text
            ))

    def signal_and_wait(self, pid, sig, frame):
        proc = psutil.Process(pid)
        #proc.send_signal(sig)

    def trigger_signal_and_wait(self, pid):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        signal.signal(signal.SIGQUIT, signal.SIG_IGN)
        signal.signal(signal.SIGINT, partial(self.signal_and_wait, pid))
        signal.signal(signal.SIGTERM, partial(self.signal_and_wait, pid))
        signal.signal(signal.SIGHUP, partial(self.signal_and_wait, pid))
        signal.signal(signal.SIGQUIT, partial(self.signal_and_wait, pid))

    def run(self, quiet=False):
        """Run all tests in the defined suite of modules."""
        tests = self.tests()
        result_list = []

        for test in tests:
            if quiet:
                hijacked_stdout = sys.stdout
                hijacked_stderr = sys.stderr
                sys.stdout = open(path.join(self.settings['engine_folder'], ".hitch", "test.out"), "ab", 0)
                sys.stderr = open(path.join(self.settings['engine_folder'], ".hitch", "test.err"), "ab", 0)

            def run_test_in_separate_process(file_descriptor_stdin, result_queue):
                """Change process group, run test and return result via a queue."""
                orig_pgid = os.getpgrp()
                os.setpgrp()
                result_queue.put("pgrp")
                sys.stdin = os.fdopen(file_descriptor_stdin)
                result = test.run()
                result_queue.put(result)
                os.tcsetpgrp(file_descriptor_stdin, orig_pgid)

            orig_stdin_termios = termios.tcgetattr(sys.stdin.fileno())
            orig_stdin_fileno = sys.stdin.fileno()
            orig_pgid = os.getpgrp()

            file_descriptor_stdin = sys.stdin.fileno()
            result_queue = multiprocessing.Queue()


            # Start new process to run test in, to isolate it from future test runs
            test_process = multiprocessing.Process(
                target=run_test_in_separate_process,
                args=(file_descriptor_stdin, result_queue)
            )

            test_timed_out = False
            test_process.start()
            #self.trigger_signal_and_wait(test_process.pid)

            # Wait until PGRP is changed
            result_queue.get()

            # Make stdin go to the test process so that you can use ipython, etc.
            os.tcsetpgrp(file_descriptor_stdin, os.getpgid(test_process.pid))

            # Wait until process has finished
            proc = psutil.Process(test_process.pid)
            test_timeout = self.settings.get("test_timeout", None)
            test_shutdown_timeout = self.settings.get("test_shutdown_timeout", 10)

            try:
                proc.wait(timeout=test_timeout)
            except psutil.TimeoutExpired:
                test_timed_out = True
                proc.send_signal(signal.SIGTERM)

                try:
                    proc.wait(timeout=test_shutdown_timeout)
                except psutil.TimeoutExpired:
                    # TODO: kill all processes
                    proc.send_signal(signal.SIGKILL)

            try:
                result = result_queue.get_nowait()
            except multiprocessing.queues.Empty:
                result = Result(test, True, 0.0)

            if test_timed_out:
                result.aborted = False
            result_list.append(result)

            if not quiet:
                try:
                    termios.tcsetattr(orig_stdin_fileno, termios.TCSANOW, orig_stdin_termios)
                except termios.error as err:
                    # I/O error caused by another test stopping this one
                    if err[0] == 5:
                        pass

            if quiet:
                sys.stdout = hijacked_stdout
                sys.stderr = hijacked_stderr

            if quiet and result is not None:
                if result.failure:
                    warn("X")
                else:
                    warn(".")

            if result.aborted:
                warn("Aborted\n")
                sys.exit(1)
        return Results(result_list)
