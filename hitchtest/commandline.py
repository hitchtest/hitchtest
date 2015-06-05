"""Command line interface to hitchtest."""
from click import command, group, argument, option
from sys import stderr, exit, executable
from os import path
import module
import signal
import yaml
import json

@command()
@argument('filename')
@option('-r', '--repeat', default=1, help='Number of times to run the test. Report % success and failure.')
@option('-s', '--settings', default=None, help="Load settings from file.")
@option('-e', '--extra', default=None, help="""Load extra vars on command line as JSON (e.g. --extra '{"postgres_version": "3.5.5"}'""")
def cli(filename, repeat, settings, extra):
    """Run test(s)"""
    # .hitch/virtualenv/bin/ < - 4 directories up from where the python exec resides
    engine_folder = path.abspath(path.join(executable, "..", "..", "..", ".."))

    if filename.endswith(".yml"):
        if settings is not None:
            with open(settings) as settingsfile_handle:
                dict_vars = yaml.load(settingsfile_handle.read())
        else:
            if path.join(path.dirname(filename), "settings.yml"):
                with open(path.join(path.dirname(filename), "settings.yml")) as settingsfile_handle:
                    dict_vars = yaml.load(settingsfile_handle.read())
            else:
                dict_vars = {}

        if extra is not None:
            dict_vars = dict(dict_vars.items() + json.loads(extra).items())

        with open(path.join(module.HITCHTEST_DIR, "unittest.jinja2")) as template_handle:
            template_code = template_handle.read()

        m = module.Module(filename, engine_folder, template_code, dict_vars)
        m.compile_to_python()
        m.run_python(executable)
    else:
        stderr.write("I didn't understand {}\n".format(filename))
        stderr.flush()
        exit(1)

def run():
    """Run hitch tests"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    cli()

if __name__ == '__main__':
    run()
