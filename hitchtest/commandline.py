"""Command line interface to hitchtest."""
from click import command, group, argument, option
from hitchtest.utils import log, warn, signals_trigger_exit
from sys import exit, executable
from os import path, walk, chdir
from hitchtest.settings import Settings
from hitchtest import module
from hitchtest import suite
import yaml as pyyaml
import fnmatch
import signal
import json


@command()
@argument('filenames', nargs=-1)
@option('-y', '--yaml', is_flag=True, help='Output the YAML tests (for debugging).')
@option('-q', '--quiet', is_flag=True, help='Quiet mode. Do not print test output to screen. (DEPRECATED)')
@option('-t', '--tags', default=None, help='Only run tests with comma-separated specified tag(s). (e.g. --tags tag-1,tag-2,tag.3)')
@option('-s', '--settings', default=None, help="Load settings from specified file.")
@option('-e', '--extra', default=None, help="""Load extra settings on command line as JSON (e.g. --extra '{"postgres_version": "3.5.5"}'""")
def cli(filenames, yaml, quiet, tags, settings, extra):
    """Run test files or entire directories containing .test files."""
    # .hitch/virtualenv/bin/python <- 4 directories up from where the python exec resides
    engine_folder = path.abspath(path.join(executable, "..", "..", "..", ".."))
    filenames = [path.abspath(path.relpath(filename, engine_folder)) for filename in filenames]
    chdir(engine_folder)

    if quiet:
        warn((
            "The --quiet switch has been deprecated. You can make your tests run quietly "
            "by setting the property quiet to True via --extra or in a settings file.\n\n"
            "See here for more details on the change : \n"
            "https://hitchtest.readthedocs.org/en/latest/faq/why_was_hitch_behavior_changed.html\n"
        ))
        exit(1)

    #new_default_settings_filename = path.join(engine_folder, "all.settings")
    #settings_filename = None if settings is None else path.join(engine_folder, settings)

    #if path.exists(new_default_settings_filename):
        #_overwrite_settings_with_yaml(new_default_settings_filename, settings_dict)

    #if settings_filename is not None:
        #if not path.exists(settings_filename):
            #warn("Settings file '{}' could not be found!\n".format(settings_filename))
            #exit(1)
        #else:
            ## Load settings from specified file, if it exists
            #_overwrite_settings_with_yaml(settings_filename, settings_dict)

    ## Load extra settings from command line JSON and overwrite what's already set
    #if extra is not None:
        #try:
            #settings_dict.update(json.loads(extra).items())
        #except ValueError as error:
            #warn("""{} in:\n ==> --extra '{}' (must be valid JSON)\n""".format(str(error), extra))
            #exit(1)
        #except AttributeError:
            #warn("""Error in:\n ==> --extra '{}' (must be valid JSON and not a list)\n""".format(extra))
            #exit(1)

    settings_dict = Settings(engine_folder, settings, extra)
    settings_dict['engine_folder'] = engine_folder
    if 'quiet' not in settings_dict:
        settings_dict['quiet'] = False

    if len(filenames) == 0:
        warn("No tests specified.\n")
        exit(1)

    # Get list of files from specified files/directories
    matches = []
    test_not_found = False
    for filename in filenames:
        if not path.exists(filename):
            warn("Test '{}' not found.\n".format(filename))
            test_not_found = True
        if path.isdir(filename):
            for root, dirnames, filenames_in_dir in walk(filename):
                for filename_in_dir in fnmatch.filter(filenames_in_dir, '*.test'):
                    if ".hitch" not in root: # Ignore everything in .hitch
                        matches.append(path.join(root, filename_in_dir))
        else:
            matches.append(filename)

    if test_not_found:
        exit(1)

    # Get list of modules from matching directly specified files from command line
    # and indirectly (in the directories of) directories specified from cmd line
    test_modules = []
    for filename in matches:
        if filename.endswith(".test"):
            test_modules.append(module.Module(filename, settings_dict))
        else:
            warn(
                "Tests must have the extension .test"
                "- '{}' doesn't have that extension\n".format(filename)
            )
            exit(1)

    test_suite = suite.Suite(test_modules, settings_dict, tags)

    if yaml:
        test_suite.printyaml()
    else:
        returned_results = test_suite.run(quiet=quiet)

        # Lines must be split to prevent stdout blocking
        result_lines = returned_results.to_template(
            template=settings_dict.get('results_template', None)
        ).split('\n')

        for line in result_lines:
            log("{}\n".format(line))

        exit(1 if len(returned_results.failures()) > 0 else 0)

def run():
    """Run hitch tests"""
    signals_trigger_exit()
    cli()

if __name__ == '__main__':
    run()
