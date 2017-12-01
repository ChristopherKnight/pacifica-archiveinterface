#!/usr/bin/python
"""HMS Sideband Backend Archive Module.

Module that implements the abstract_backend_archive class for a HMS Sideband
backend.
"""
import os
import shutil
from archiveinterface.archive_utils import un_abs_path, read_config_value
from archiveinterface.archive_interface_error import ArchiveInterfaceError
from archiveinterface.archivebackends.oracle_hms_sideband.extended_hms_sideband import (
    ExtendedHmsSideband)
from archiveinterface.archivebackends.abstract.abstract_backend_archive \
    import AbstractBackendArchive
from archiveinterface.id2filename import id2filename


def path_info_munge(filepath):
    """Munge the path for this filetype."""
    return_path = un_abs_path(id2filename(int(filepath)))
    return return_path


class HmsSidebandBackendArchive(AbstractBackendArchive):
    """HMS Sideband Backend Archive Class.

    Class that implements the abstract base class for the hms sideband
    archive interface backend.
    """

    def __init__(self, prefix):
        """Constructor for HMS Sideband Backend Archive."""
        super(HmsSidebandBackendArchive, self).__init__(prefix)
        self._prefix = prefix
        self._file = None
        self._fpath = None
        self._filepath = None
        # since the database prefix may be different then the system the file is mounted on
        self._sam_qfs_prefix = read_config_value('hms_sideband', 'sam_qfs_prefix')

    def open(self, filepath, mode):
        """Open a hms sideband file."""
        # want to close any open files first
        try:
            if self._file:
                self.close()
        except ArchiveInterfaceError as ex:
            err_str = "Can't close previous HMS Sideband file before opening new "\
                      'one with error: ' + str(ex)
            raise ArchiveInterfaceError(err_str)
        try:
            self._fpath = un_abs_path(filepath)
            filename = os.path.join(self._prefix, path_info_munge(self._fpath))
            self._filepath = filename
            # path database refers to, rather then just the file system mount path
            sam_qfs_path = os.path.join(self._sam_qfs_prefix, path_info_munge(self._fpath))
            self._file = ExtendedHmsSideband(self._filepath, mode, sam_qfs_path)
            return self
        except Exception as ex:
            err_str = "Can't open HMS Sideband file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def close(self):
        """Close a HMS Sideband file."""
        try:
            if self._file:
                self._file.close()
                self._file = None
        except Exception as ex:
            err_str = "Can't close HMS Sideband file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def read(self, blocksize):
        """Read a HMS Sideband file."""
        try:
            if self._file:
                return self._file.read(blocksize)
        except Exception as ex:
            err_str = "Can't read HMS SIdeband file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def write(self, buf):
        """Write a HMS Sideband file to the archive."""
        try:
            if self._file:
                return self._file.write(buf)
        except Exception as ex:
            err_str = "Can't write HMS Sideband file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def set_mod_time(self, mod_time):
        """Set the mod time on a HMS file."""
        try:
            if self._filepath:
                os.utime(self._filepath, (mod_time, mod_time))
        except Exception as ex:
            err_str = "Can't set HMS Sideband file mod time with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def set_file_permissions(self):
        """Set the file permissions for a posix file."""
        try:
            if self._filepath:
                os.chmod(self._filepath, 0444)
        except Exception as ex:
            err_str = "Can't set HMS Sideband file permissions with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def stage(self):
        """Stage a HMS Sideband file."""
        try:
            if self._file:
                return self._file.stage()
        except Exception as ex:
            err_str = "Can't stage HMS Sideband file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def status(self):
        """Get the status of a HMS Sideband file."""
        try:
            if self._file:
                return self._file.status()
        except Exception as ex:
            err_str = "Can't get HMS Sideband file status with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def patch(self, file_id, old_path):
        """Move a hms file."""
        try:
            fpath = un_abs_path(file_id)
            new_filepath = os.path.join(self._prefix, path_info_munge(fpath))
            new_directories = os.path.dirname(new_filepath)
            if not os.path.exists(new_directories):
                os.makedirs(new_directories)

            shutil.move(old_path, new_filepath)
        except Exception as ex:
            err_str = "Can't move posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
