from os import path, getpgrp, getpgid, tcsetpgrp, fdopen
from hitchtest.results import Results
import multiprocessing
import signal
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
            sys.stdout.write("\n# {}\n{}\n".format(
                test_module.filename,
                test_module.test_yaml_text
            ))

    def run(self, quiet=False):
        """Run all tests in the defined suite of modules."""
        tests = self.tests()
        result_list = []

        for test in tests:
            if quiet:
                hijacked_stdout = sys.stdout
                hijacked_stderr = sys.stderr
                sys.stdout = open(path.join(self.settings['engine_folder'], ".hitch", "test.out"), "a", 0)
                sys.stderr = open(path.join(self.settings['engine_folder'], ".hitch", "test.err"), "a", 0)

            def run_in_separate_process(fdin, child_queue, result_queue):
                orig_pgid = os.getpgrp()
                os.setpgrp()
                child_queue.put(os.getpgrp())
                sys.stdin = os.fdopen(fdin)
                result = test.run()
                os.tcsetpgrp(fdin, orig_pgid)
                result_queue.put(result)

            fdin = sys.stdin.fileno()
            child_queue = multiprocessing.Queue()
            result_queue = multiprocessing.Queue()
            p = multiprocessing.Process(
                target=run_in_separate_process,
                args=(fdin, child_queue, result_queue)
            )
            p.start()
            child_pid = child_queue.get()
            child_pgid = os.getpgid(child_pid)
            os.tcsetpgrp(fdin, child_pgid)
            result = result_queue.get()
            result_list.append(result)

            os.kill(p.pid, signal.SIGKILL)

            if quiet:
                sys.stdout = hijacked_stdout
                sys.stderr = hijacked_stderr

            if quiet and result is not None:
                if result.failure:
                    sys.stderr.write("X")
                else:
                    sys.stderr.write(".")

            if result is None:
                sys.stderr.write("ABORT\n")
                sys.exit(1)
        return Results(result_list)
