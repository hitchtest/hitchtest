from hitchtest.utils import warn
from os.path import join, exists
from sys import exit
import yaml as pyyaml
import json


class Settings(object):
    def __init__(self, engine_directory, override_settings_filename, extra_string):
        
        if exists(join(engine_directory, "settings.yml")):
            warn((
                "settings.yml as a 'default settings' file has been deprecated. "
                "Rename to all.settings instead:\n\n"
                "See here for more details on the change : \n"
                "https://hitchtest.readthedocs.org/en/latest/faq/why_was_hitch_behavior_changed.html\n"
            ))
            exit(1)

        self.settings_dict = {}
        
        full_override_settings_filename = None if override_settings_filename is None else join(engine_directory, override_settings_filename)

        if exists(join(engine_directory, "all.settings")):
            self._overwrite_settings_with_yaml(join(engine_directory, "all.settings"))

        if override_settings_filename is not None:
            if not exists(override_settings_filename):
                warn("Settings file '{}' could not be found!\n".format(override_settings_filename))
                exit(1)
            else:
                # Load settings from specified file, if it exists
                self._overwrite_settings_with_yaml(override_settings_filename)

        # Load extra settings from command line JSON and overwrite what's already set
        if extra_string is not None:
            try:
                self.settings_dict.update(json.loads(extra_string).items())
            except ValueError as error:
                warn("""{} in:\n ==> --extra '{}' (must be valid JSON)\n""".format(str(error), extra_string))
                exit(1)
            except AttributeError:
                warn("""Error in:\n ==> --extra '{}' (must be valid JSON and not a list)\n""".format(extra_string))
                exit(1)

    def __getitem__(self, key):
        if key not in self.settings_dict:
            raise IndexError
        return self.settings_dict[key]

    def get(self, key, default_value=None):
        if key not in self.settings_dict:
            return default_value
        else:
            return self.settings_dict[key]

    def __setitem__(self, key, value):
        self.settings_dict[key] = value

    def as_dict(self):
        return self.settings_dict

    def _overwrite_settings_with_yaml(self, settings_filename):
        """Load YAML and overwrite """
        if exists(settings_filename):
            with open(settings_filename) as settingsfile_handle:
                settingsfile_contents = settingsfile_handle.read()

            try:
                self.settings_dict.update(pyyaml.load(settingsfile_contents))
            except pyyaml.parser.MarkedYAMLError as error:
                warn("YAML parser error in {}:\n{}\nError:{}\n".format(
                    settings_filename, settingsfile_contents, str(error),
                ))
                exit(1)
            except ValueError:
                warn("YAML parser error in {}. Should be associative array not list:\n\n{}\n".format(
                    settings_filename, settingsfile_contents,
                ))
                exit(1)
