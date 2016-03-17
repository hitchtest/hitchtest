from hitchtest.environment.utils import version_comparison, return_code_zero, check_output_lines
from collections import Counter
import unixpackage
import struct
import psutil
import glob
import sys
import re
import os


class HitchEnvironmentException(Exception):
    pass


def freeports(required_ports):
    """Verifies that none of the required_ports are not in use. Raise exception if they are."""
    unusable_ports = []
    import socket
    for port in required_ports:
        socket_to_try = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_to_try.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            socket_to_try.bind(('', port))
            socket_to_try.listen(1)
        except socket.error as e:
            unusable_ports.append(str(port))
        finally:
            socket_to_try.close()

    if len(unusable_ports) > 0:
        raise HitchEnvironmentException(
            "Required network port(s): {} not usable.".format(', '.join(unusable_ports))
        )


def packages(package_list):
    """Verify that a list of unixpackage packages are installed."""
    if not unixpackage.packages_installed(package_list):
        raise HitchEnvironmentException((
            "The following packages are required: {}.\n"
            "The command to install them on this environment is: {}.\n"
        ).format(', '.join(package_list), unixpackage.install_command(package_list)))


def debs(packages):
    """Verify that a list of debs are installed. Ignore if not a deb based system."""
    if len(packages) > 10:
        debs(packages[10:])
        packages = packages[:10]
    if return_code_zero(["which", "dpkg"]):
        if not return_code_zero(["dpkg", "--list",] + packages):
            raise HitchEnvironmentException(
                "sudo apt-get install {} : required for test to run".format(' '.join(packages))
            )


def brew(packages):
    """Verify that a list of brew packages are installed. Ignore if not a mac."""
    if sys.platform == "darwin":
        version_list = [
            x for x in check_output_lines(["brew", "list", "--versions"] + packages) if x != ""
        ]
        if len(version_list) < len(packages):
            raise HitchEnvironmentException(
                "brew install {} : required for test to run".format(' '.join(packages))
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


def x_available(true_or_false):
    """Checks if DISPLAY enviroment variable is set, hence that X is available."""
    if "DISPLAY" not in os.environ:
        raise HitchEnvironmentException(
            """The DISPLAY environment variable is not set. See """
            """https://stackoverflow.com/questions/784404/how-can-i-specify-a-display """
            """for more details about what to do to fix this issue."""
        )


def i_am_root(true_or_false):
    """Verify that the user running this test either is, or is not, root."""
    import getpass
    if getpass.getuser() == "root" and not true_or_false:
        raise HitchEnvironmentException(
            """The current user is root. You must run hitch clean and then """
            """try running the test(s) again as a non-root user."""
        )

    if getpass.getuser() != "root" and true_or_false:
        raise HitchEnvironmentException(
            """The current user is *not* root. You must run hitch clean and then """
            """try running the test(s) again as the root user."""
        )


def need_free_inotify_watches(number_of_watches_needed):
    """
    Verify that enough inotify watches are available. Raise exception if they are not.

    Only valid on linux, so skipped on non-linux platforms.
    """
    from path import Path
    if "linux" in sys.platform:
        max_user_watches = int(
            Path("/proc/sys/fs/inotify/max_user_watches").bytes().decode('utf8').replace('\n', '')
        )

        existing_user_watches = len([
            fulllink for fulllink in (os.readlink(x) for x in glob.glob("/proc/*/fd/*")
                if os.path.exists(x)) if "inotify" in fulllink
        ])

        if max_user_watches - existing_user_watches < number_of_watches_needed:
            raise HitchEnvironmentException((
                "You must increase max_user_watches in order to run your tests.\n\n"
                "Number of inotify watches required: {}\n"
                "Number of inotify watches left: {}\n"
                "Max user watches: {}\n"
                "How to temporarily raise number of watches:\n\n"
                "  sudo echo 16384 > /proc/sys/fs/inotify/max_user_watches\n\n"
                "How to permanently raise the number of watches:\n\n"
                "  Add the line 'fs.inotify.max_user_watches=16384' to the end of /etc/sysctl.conf"
            ).format(
                number_of_watches_needed,
                max_user_watches - existing_user_watches,
                max_user_watches,
            ))


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
# TODO : nslookup -timeout=1 microsoft.com


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
