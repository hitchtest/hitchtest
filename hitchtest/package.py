
class HitchPackage(object):
    def __init__(self):
        pass

    def _download(self, name, url):
        pass

    def _extract_archive(self, filename, destination):
        pass

    def build(self):
        pass

    def verify(self):
        pass

class PackageNotBuilt(Exception):
    pass

class PackageVerificationFailure(Exception):
    pass

class InvalidPackageVersion(Exception):
    pass
