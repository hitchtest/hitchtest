"""Command line interface to hitchtest."""
from click import command, group, argument, option
from hitchtest.utils import log, warn, signals_trigger_exit
from sys import exit, executable
from os import path, walk, chdir
from hitchtest import module
from hitchtest import suite
import yaml as pyyaml
import fnmatch
import signal
import json


# TODO : Remove --results and put the setting in to settings instead.

@command()
@argument('filenames', nargs=-1)
@option('-y', '--yaml', is_flag=True, help='Output the YAML tests (for debugging).')
@option('-q', '--quiet', is_flag=True, help='Quiet mode. Do not print test output to screen.')
@option('-r', '--results', default=None, help='Specify a template to display test results with.')
@option('-s', '--settings', default=None, help="Load settings from specified file.")
@option('-e', '--extra', default=None, help="""Load extra settings on command line as JSON (e.g. --extra '{"postgres_version": "3.5.5"}'""")
def cli(filenames, yaml, quiet, results, settings, extra):
    """Run test files or entire directories containing .test files."""
    # .hitch/virtualenv/bin/python <- 4 directories up from where the python exec resides
    engine_folder = path.abspath(path.join(executable, "..", "..", "..", ".."))
    settings_dict = {'engine_folder': engine_folder, 'quiet': quiet, }
    filenames = [path.relpath(filename, engine_folder) for filename in filenames]
    chdir(engine_folder)
    default_settings_filename = path.join(engine_folder, "settings.yml")
    settings_filename = default_settings_filename if settings is None else path.join(engine_folder, settings)

    if settings is not None and not path.exists(settings_filename):
        warn("Settings file '{}' could not be found!\n".format(settings_filename))
        sys.exit(1)

    # Load settings from file, if it exists
    if path.exists(settings_filename):
        with open(settings_filename) as settingsfile_handle:
            settings_dict.update(pyyaml.load(settingsfile_handle.read()))

    # Load extra settings from command line JSON
    if extra is not None:
        settings_dict.update(json.loads(extra).items())


    # Get list of files from specified files/directories
    matches = []
    for filename in filenames:
        if path.isdir(filename):
            for root, dirnames, filenames_in_dir in walk(filename):
                for filename_in_dir in fnmatch.filter(filenames_in_dir, '*.test'):
                    matches.append(path.join(root, filename_in_dir))
        else:
            matches.append(filename)

    # Get list of modules from matching directly specified files from command line
    # and indirectly (in the directories of) directories specified from cmd line
    test_modules = []
    for filename in matches:
        if filename.endswith(".test"):
            test_modules.append(module.Module(filename, settings_dict))
        else:
            warn("I didn't understand {}\n".format(filename))
            exit(1)

    test_suite = suite.Suite(test_modules, settings_dict)

    if yaml:
        test_suite.printyaml()
    else:
        returned_results = test_suite.run(quiet=quiet)
        log(returned_results.to_template(template=results))
        exit(1 if len(returned_results.failures()) > 0 else 0)

def run():
    """Run hitch tests"""
    signals_trigger_exit()
    cli()

if __name__ == '__main__':
    run()
