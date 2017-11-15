#!/usr/bin/python
"""Posix Backend Archive Module.

Module that implements the abstract_backend_archive class for a posix
backend.
"""

import os
import shutil
from archiveinterface.archive_utils import un_abs_path, read_config_value
from archiveinterface.id2filename import id2filename
from archiveinterface.archive_interface_error import ArchiveInterfaceError
from archiveinterface.archivebackends.posix.extendedfile import ExtendedFile
from archiveinterface.archivebackends.abstract.abstract_backend_archive \
    import AbstractBackendArchive


class PosixBackendArchive(AbstractBackendArchive):
    """Posix Backend Archive Class.

    Class that implements the abstract base class for the posix
    archive interface backend.
    """

    def __init__(self, prefix):
        """Constructor for Posix Backend Archive."""
        super(PosixBackendArchive, self).__init__(prefix)
        self._prefix = prefix
        self._file = None
        self._filepath = None

    def open(self, filepath, mode):
        """Open a posix file."""
        # want to close any open files first
        try:
            if self._file:
                self.close()
        except ArchiveInterfaceError as ex:
            err_str = "Can't close previous posix file before opening new "\
                      'one with error: ' + str(ex)
            raise ArchiveInterfaceError(err_str)
        try:
            if read_config_value('posix', 'use_id2filename') == 'true':
                fpath = un_abs_path(id2filename(int(un_abs_path(filepath))))
            else:
                fpath = un_abs_path(filepath)
            filename = os.path.join(self._prefix, fpath)
            self._filepath = filename
            new_directories = os.path.dirname(filename)
            if not os.path.exists(new_directories):
                os.makedirs(new_directories)
            self._file = ExtendedFile(self._filepath, mode)
            return self
        except Exception as ex:
            err_str = "Can't open posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def close(self):
        """Close a posix file."""
        try:
            if self._file:
                self._file.close()
                self._file = None
        except Exception as ex:
            err_str = "Can't close posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def read(self, blocksize):
        """Read a posix file."""
        try:
            if self._file:
                return self._file.read(blocksize)
        except Exception as ex:
            err_str = "Can't read posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def write(self, buf):
        """Write a posix file to the archive."""
        try:
            if self._file:
                return self._file.write(buf)
        except Exception as ex:
            err_str = "Can't write posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def set_mod_time(self, mod_time):
        """Set the mod time on a posix file."""
        try:
            if self._filepath:
                os.utime(self._filepath, (mod_time, mod_time))
        except Exception as ex:
            err_str = "Can't set posix file mod time with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def set_file_permissions(self):
        """Set the file permissions for a posix file."""
        try:
            if self._filepath:
                os.chmod(self._filepath, 0444)
        except Exception as ex:
            err_str = "Can't set posix file permissions with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def stage(self):
        """Stage a posix file (no-opt essentially)."""
        try:
            if self._file:
                return self._file.stage()
        except Exception as ex:
            err_str = "Can't stage posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def status(self):
        """Get the status of a posix file."""
        try:
            if self._file:
                return self._file.status()
        except Exception as ex:
            err_str = "Can't get posix file status with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def patch(self, file_id, old_path):
        """Move a posix file."""
        try:
            if read_config_value('posix', 'use_id2filename') == 'true':
                fpath = un_abs_path(id2filename(int(un_abs_path(file_id))))
            else:
                fpath = un_abs_path(file_id)
            new_filepath = os.path.join(self._prefix, fpath)
            new_directories = os.path.dirname(new_filepath)
            if not os.path.exists(new_directories):
                os.makedirs(new_directories)

            shutil.move(old_path, new_filepath)
        except Exception as ex:
            err_str = "Can't move posix file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
