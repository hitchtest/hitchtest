from os import path, makedirs
from hitchtest.utils import get_hitch_directory
import json


def is_modified(includes, excludes=None):
    """Return True if matching file(s) are either modified or no record of them being modified is kept."""

    # If checking just for one file, make it a list
    if type(includes) is str:
        includes = [includes, ]

    if excludes is None:
        excludes = []

    modififications_filename = path.join(get_hitch_directory(), "modified.json")
    
    if path.exists(modififications_filename):
        with open(modififications_filename, 'r') as modifications_filename_handle:
            modifications = json.loads(modifications_filename_handle.read())
    else:
        modifications = {}

    at_least_one_modified = False

    filenames = list(set(includes) - set(excludes))
    
    for filename in filenames:
        modified_time = path.getmtime(filename)
        
        if filename in modifications:
            if modified_time > modifications[filename]:
                modifications[filename] = modified_time
                at_least_one_modified = True
        else:
            modifications[filename] = modified_time
            at_least_one_modified = True

    with open(modififications_filename, 'w') as modifications_file_handle:
        modifications_file_handle.write(json.dumps(modifications))

    return at_least_one_modified
