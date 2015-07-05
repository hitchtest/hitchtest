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
        self.hitch_dir = path.abspath(
            path.join(path.dirname(sys.executable), "..", "..")
        )

        if self.name is None:
            raise PackageVerificationFailure("This package does not have self.name set!")

    def get_build_directory(self):
        build_directory = path.join(self.hitch_dir, "build")
        if not path.exists(build_directory):
            makedirs(build_directory)
        return build_directory

    def get_downloads_directory(self):
        downloads_directory = path.join(self.hitch_dir, "downloads")
        if not path.exists(downloads_directory):
            makedirs(downloads_directory)
        return downloads_directory

    def check_version(self, version, versions_list, issues_url, name=None):
        package_name = self.name if name is None else name
        if version not in versions_list:
            raise InvalidPackageVersion(
                "{} version {} not in list of approved versions: \n{}\n"
                "Raise a ticket at {} "
                "if you think it should be.".format(package_name, version, versions_list, issues_url)
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
