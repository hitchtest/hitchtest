from commandlib import Commands
from os import path, makedirs
import sys


class PackageNotBuilt(Exception):
    pass

class PackageVerificationFailure(Exception):
    pass

class InvalidPackageVersion(Exception):
    pass


class HitchPackage(object):
    name = None

    def __init__(self):

        # 3 directories above virtualenv python binary is the hitchdir
        self.hitch_package_directory = path.abspath(
            path.join(path.expanduser("~"), ".hitchpkg")
        )

        if self.name is None:
            raise PackageVerificationFailure("This package does not have self.name set!")

    def get_build_directory(self):
        if not path.exists(self.hitch_package_directory):
            makedirs(self.hitch_package_directory)
        return self.hitch_package_directory

    def get_downloads_directory(self):
        if not path.exists(self.hitch_package_directory):
            makedirs(self.hitch_package_directory)
        return self.hitch_package_directory

    def check_version(self, version, versions_list, issues_url, name=None):
        package_name = self.name if name is None else name
        if str(version) not in versions_list:
            raise InvalidPackageVersion(
                "{} version {} not in list of approved versions: \n{}\n"
                "Raise a ticket at {} "
                "if you think it should be.".format(
                    package_name, version, versions_list, issues_url
                )
            )
        return version

    def download_file(self, name, url):
        pass

    def extract_archive(self, filename, destination):
        pass

    def build(self):
        pass

    def verify(self):
        pass
    
    @property
    def cmd(self):
        return Commands(self.bin_directory)
