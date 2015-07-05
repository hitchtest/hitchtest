from subprocess import call, check_output, PIPE
import re

def check_output_lines(command):
    return check_output(command).decode('utf8').split('\n')

def return_code_zero(command):
    """Returns True if command called has return code zero."""
    return call(command, stdout=PIPE, stderr=PIPE) == 0

def versiontuple(v):
    return tuple(map(int, (v.split("."))))

def version_comparison(version_check, version):
    match = re.compile("((?:\>|\=|\<)\=?)?(.*)").match(version_check)
    comparison = match[0]
    version_to_check = match[1]

    if match == "":
        return versiontuple(version_to_check) == versiontuple(version)
    elif match == "=":
        return versiontuple(version_to_check) == versiontuple(version)
    elif match == "==":
        return versiontuple(version_to_check) == versiontuple(version)
    elif match == "<=":
        return versiontuple(version_to_check) <= versiontuple(version)
    elif match == "<":
        return versiontuple(version_to_check) < versiontuple(version)
    elif match == ">":
        return versiontuple(version_to_check) > versiontuple(version)
    elif match == ">=":
        return versiontuple(version_to_check) >= versiontuple(version)
    else:
        raise RuntimeError("Couldn't understand {}".format(version_check))

