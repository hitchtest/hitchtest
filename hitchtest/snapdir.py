from subprocess import check_call
from os import path, makedirs, listdir, sep


def snapshot(source, destination, name=None):
    """Snapshot one directory to another. Specify names to snapshot small, named differences."""
    source = source + sep
    destination = destination + sep

    if not path.isdir(source):
        raise RuntimeError("source is not a directory")

    if path.exists(destination):
        if not path.isdir(destination):
            raise RuntimeError("destination is not a directory")

        if name is None:
            raise RuntimeError("can't snapshot base snapshot if destination exists")

    snapdir = path.join(destination, ".snapdir")
    
    if path.exists(path.join(source, ".snapdir")):
        raise RuntimeError("snapdir exists in source directory")

    if name is None:
        check_call(["rsync", "--del", "-av", source, destination])
        makedirs(snapdir)
    else:
        if not path.exists(snapdir):
            raise RuntimeError("No snapdir in destination directory")

        check_call(["rsync", "--del", "-av", "--only-write-batch={}".format(path.join(snapdir, name)), source, destination])


def restore(destination, source, name=None):
    """Restore snapshots from one directory to another."""
    source = source + sep
    destination = destination + sep

    snapdir = path.join(destination, ".snapdir")

    check_call(["rsync", "--progress", "--del", "--exclude=.snapdir", "-av", destination, source])

    if name is not None:
        check_call(["rsync", "--del", "--exclude=.snapdir", "-av", "--read-batch={}".format(path.join(snapdir, name)), destination, source])
