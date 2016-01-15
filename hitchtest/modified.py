from os import path, makedirs
from hitchtest.utils import get_hitch_directory
import json

class is_modified(object):
    def __init__(self, includes, excludes=None):
        self.includes = [includes, ] if type(includes) is str else includes
        self.excludes = excludes if excludes is not None else []
        self.modififications_filename = path.join(get_hitch_directory(), "modified.json")
    
    def __enter__(self):
        # Get all existing modification timestamps
        if path.exists(self.modififications_filename):
            with open(self.modififications_filename, 'r') as handle:
                self.modifications = json.loads(handle.read())
        else:
            self.modifications = {}

        at_least_one_modified = False

        # Total list of filenames
        filenames = list(set(self.includes) - set(self.excludes))

        # Check if any of the files have been updated since
        for relfilename in filenames:
            absfilename = path.abspath(relfilename)
            modified_time = path.getmtime(absfilename)
            
            if absfilename in self.modifications:
                if modified_time > self.modifications[absfilename]:
                    self.modifications[absfilename] = modified_time
                    at_least_one_modified = True
            else:
                self.modifications[absfilename] = modified_time
                at_least_one_modified = True

        return at_least_one_modified

    def __exit__(self, type, value, traceback):
        # If an exception is thrown, don't update modifications
        if traceback is None:
            # Check for modifications by nested modification checkers
            if path.exists(self.modififications_filename):
                with open(self.modififications_filename, 'r') as handle:
                    updated_modifications = json.loads(handle.read())
            else:
                updated_modifications = {}

            # If a modification has been updated since __enter__, don't overwrite it
            for filename in updated_modifications:
                if updated_modifications[filename] > self.modifications[filename]:
                    self.modifications[filename] = updated_modifications[filename]
            
            with open(self.modififications_filename, 'w') as handle:
                handle.write(json.dumps(self.modifications))
