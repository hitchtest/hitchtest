from hitchtest.environment.utils import version_comparison, return_code_zero, check_output_lines
from collections import Counter
from os import path
import struct
import sys
import re

class HitchEnvironmentException(Exception):
    pass

def freeports(required_ports):
    """Verifies that none of the required_ports are not in use. Raise exception if they are."""
    # TODO: Harden this code up a bit
    lines = [line for line in check_output_lines(["netstat", "-ln"]) if line.startswith("tcp")]
    used_ports = []

    for line in lines:
        columns = [col for col in line.split(" ") if col != ""]
        used_ports.append(int(columns[3].split(":")[1]))

    overlap = list((Counter(used_ports) & Counter(required_ports)).elements())
    in_use = ', '.join([str(port) for port in overlap])
    if len(overlap) > 0:
        raise HitchEnvironmentException(
            "Required network port(s) {} currently in use.".format(in_use)
        )

def debs(packages):
    """Verify that a list of debs are installed. Ignore if not a deb based system."""
    if return_code_zero(["which", "dpkg"]):
        if not return_code_zero(["dpkg", "--list",] + packages):
            raise HitchEnvironmentException(
                "sudo apt-get install {} : required for test to run".format(' '.format(packages))
            )

def brew(packages):
    """Verify that a list of brew packages are installed. Ignore if not a mac."""
    if sys.platform == "darwin":
        if not return_code_zero(["brew", "list",] + packages):
            raise HitchEnvironmentException(
                "brew install {} : required for test to run".format(' '.format(packages))
            )

def systembits(bits):
    """Verify that a system is 64 or 32 bit."""
    if not bits == struct.calcsize("P") * 8:
        raise HitchEnvironmentException(
            "{} bit system required to run test. This system is {} bit".format(str(bits))
        )

def internet_detected_after(timeout):
    """Verify that a system is connected to the internet."""
    if not return_code_zero(["ping", "-c", "1", "-W", str(timeout), "8.8.8.8"]):
        raise HitchEnvironmentException(
            "No internet detected after {} seconds. Ping failed.".format(timeout)
        )

def approved_platforms(platforms):
    """Verify that the test is running on an approved platform."""
    if not sys.platform in platforms:
        raise HitchEnvironmentException(
            "This platform is {}. This test will only run on {}.".format(' '.format(platforms))
        )


# TODO : rpm package availability.
# TODO : arch package availability.
# TODO : all other package managers
# TODO : Kernel SHMMAX, glibc version, CPU usage,
# TODO : psutil.phymem_usage().available / 1024 / 1024
# TODO : psutil.cpu_percent()
# TODO : psutil.cpu_count()
# TODO : Linux Kernel version
# TODO : Mac OS X kernel version
# TODO : ulimit
# TODO : nslookup -timeout=0.1 microsoft.com


#def linux_distro(distros):
    #if path.exists("/etc/issue"):
        #with open("/etc/issue", "r") as issue_handle:
            #issue = issue_handle.read()

        #if "ubuntu" in distros and issue.startswith("Ubuntu"):
            #return True
        #if "redhat" in distros and issue.startswith("Red Hat"):
            #return True
        #return False
    #return True

#def ubuntu_version(version_check):
    #if path.exists("/etc/issue"):
        #with open("/etc/issue", "r") as issue_handle:
            #issue = issue_handle.read()
        #version = re.search("[0-9]+\.[0-9]+\.?[0-9]*", issue).group(0)
        #return version_comparison(version_check, version)
    #return True
