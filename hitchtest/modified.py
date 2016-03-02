from os import path, makedirs
from hitchtest.utils import get_hitch_directory
from path import Path
import json


HOW_TO_USE_MODIFICATION_CHECKER = """\
You cannot treat monitor as a boolean.

It must be used as a context manager like so:

from hitchtest import monitor

with monitor([filename1, filename2...]) as changed:
    if changed:
        # run command
    else:
        # don't run command
"""


class Changed(object):
    """
    Object representation of what the monitor has changed.
    
    len(changes) == number of files changed
    if changes: -> True if at least one file has changed
    
    for change in changes:
        print(change)
    """
    def __init__(self, filenames):
        self._filenames = filenames
    
    def __len__(self):
        return len(self._filenames)
    
    def __getitem__(self, index):
        return Path(self._filenames[index])
    
    def __nonzero__(self):
        return len(self._filenames) > 0
    
    def __bool__(self):
        return len(self._filenames) > 0
    
    


class monitor(object):
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

        list_of_modified_filenames = []

        # Total list of filenames
        filenames = list(set(self.includes) - set(self.excludes))

        # Check if any of the files have been updated since
        for relfilename in filenames:
            absfilename = path.abspath(relfilename)
            modified_time = path.getmtime(absfilename)
            
            if absfilename in self.modifications:
                if modified_time > self.modifications[absfilename]:
                    self.modifications[absfilename] = modified_time
                    list_of_modified_filenames.append(absfilename)
            else:
                self.modifications[absfilename] = modified_time
                list_of_modified_filenames.append(absfilename)

        return Changed(list_of_modified_filenames)

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

    def __bool__(self):
        raise NotImplementedError(HOW_TO_USE_MODIFICATION_CHECKER)

    def __nonzero__(self):
        raise NotImplementedError(HOW_TO_USE_MODIFICATION_CHECKER)
    
is_modified = monitor