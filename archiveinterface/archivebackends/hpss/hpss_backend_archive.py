#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module that implements the Abstract backend archive for an hpss backend."""
import os
import sys
from ctypes import cdll, c_void_p, create_string_buffer, c_char_p, cast
from archiveinterface.archive_utils import un_abs_path, read_config_value
from archiveinterface.archive_interface_error import ArchiveInterfaceError
from archiveinterface.archivebackends.abstract.abstract_backend_archive import (
    AbstractBackendArchive)
from archiveinterface.id2filename import id2filename

# Due to an update in hpss version we need to lazy load the linked
# c types.  Doing this with dlopen flags. 8 is the UNIX flag Integer for
# RTLD_DEEPBIND.
# RTLD_LAZY is defined as 1 in a Unix environment

RTLD_LAZY = 1
RTLD_DEEPBIND = 8
# pylint: disable=no-member
sys.setdlopenflags(RTLD_LAZY | RTLD_DEEPBIND)
# pylint: enable=no-member
# import cant be at top due to lazy load
# pylint: disable=wrong-import-position
from archiveinterface.archivebackends.hpss.hpss_extended import HpssExtended  # noqa: E402
# pylint: enable=wrong-import-position

# place where hpss lib is installed on a unix machine
HPSS_LIBRARY_PATH = '/opt/hpss/lib/libhpss.so'
# HPSS Values from their documentation
HPSS_AUTHN_MECH_INVALID = 0
HPSS_AUTHN_MECH_KRB5 = 1
HPSS_AUTHN_MECH_UNIX = 2
HPSS_AUTHN_MECH_GSI = 3
HPSS_AUTHN_MECH_SPKM = 4

HPSS_RPC_CRED_SERVER = 1
HPSS_RPC_CRED_CLIENT = 2
HPSS_RPC_CRED_BOTH = 3

HPSS_RPC_AUTH_TYPE_INVALID = 0
HPSS_RPC_AUTH_TYPE_NONE = 1
HPSS_RPC_AUTH_TYPE_KEYTAB = 2
HPSS_RPC_AUTH_TYPE_KEYFILE = 3
HPSS_RPC_AUTH_TYPE_KEY = 4
HPSS_RPC_AUTH_TYPE_PASSWD = 5


def path_info_munge(filepath):
    """Munge the path for this filetype."""
    return_path = un_abs_path(id2filename(int(filepath)))
    return return_path


class HpssBackendArchive(AbstractBackendArchive):
    """The HPSS implementation of the backend archive."""

    def __init__(self, prefix):
        """Constructor for the HPSS Backend Archive."""
        super(HpssBackendArchive, self).__init__(prefix)
        self._prefix = prefix
        self._user = read_config_value('hpss', 'user')
        self._auth = read_config_value('hpss', 'auth')
        self._file = None
        self._filepath = None
        self._hpsslib = None
        self._latency = 5  # number not significant
        # need to load  the hpss libraries/ extensions
        try:
            self._hpsslib = cdll.LoadLibrary(HPSS_LIBRARY_PATH)
        except Exception as ex:
            err_str = "Can't load hpss libraries with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)
        # need to authenticate with hpss
        try:
            self.authenticate()
        except Exception as ex:
            err_str = "Can't authenticate with hpss, error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def open(self, filepath, mode):
        """Open an hpss file."""
        # want to close any open files first
        try:
            if self._file:
                self.close()
        except ArchiveInterfaceError as ex:
            err_str = "Can't close previous hpss file before "\
                      'opening new one with error: ' + str(ex)
            raise ArchiveInterfaceError(err_str)

        # try to open file
        try:
            fpath = un_abs_path(filepath)
            filename = os.path.join(self._prefix, path_info_munge(fpath))
            self._filepath = filename
            hpss = HpssExtended(self._filepath, self._latency)
            hpss.ping_core()
            hpss.makedirs()
            hpss_fopen = self._hpsslib.hpss_Fopen
            hpss_fopen.restype = c_void_p
            self._file = hpss_fopen(filename, mode)
            if self._file < 0:
                err_str = 'Failed opening Hpss File, code: ' + str(self._file)
                raise ArchiveInterfaceError(err_str)
            return self
        except Exception as ex:
            err_str = "Can't open hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def close(self):
        """Close an HPSS File."""
        try:
            if self._file:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core()
                rcode = self._hpsslib.hpss_Fclose(self._file)
                if rcode < 0:
                    err_str = 'Failed to close hpss file with code: ' + \
                        str(rcode)
                    raise ArchiveInterfaceError(err_str)
                self._file = None
        except Exception as ex:
            err_str = "Can't close hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def read(self, blocksize):
        """Read a file from the hpss archive."""
        try:
            if self._filepath:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core()
                buf = create_string_buffer('\000' * blocksize)
                rcode = self._hpsslib.hpss_Fread(buf, 1, blocksize, self._file)
                if rcode < 0:
                    err_str = 'Failed During HPSS Fread,'\
                              'return value is: ' + str(rcode)
                    raise ArchiveInterfaceError(err_str)
                return buf.raw[:rcode]
        except Exception as ex:
            err_str = "Can't read hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def write(self, buf):
        """Write a file to the hpss archive."""
        try:
            if self._filepath:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core()
                buf_char_p = cast(buf, c_char_p)
                rcode = self._hpsslib.hpss_Fwrite(
                    buf_char_p, 1, len(buf), self._file
                )
                if rcode != len(buf):
                    raise ArchiveInterfaceError('Short write for hpss file')
        except Exception as ex:
            err_str = "Can't write hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def stage(self):
        """Stage an hpss file to the top level drive."""
        try:
            if self._filepath:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core()
                hpss.stage()
        except Exception as ex:
            err_str = "Can't stage hpss file with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def status(self):
        """Get the status of a file in the hpss archive."""
        try:
            if self._filepath:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core()
                return hpss.status()
        except Exception as ex:
            err_str = "Can't get hpss status with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def set_mod_time(self, mod_time):
        """Set the mod time for an hpss archive file."""
        try:
            if self._filepath:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core()
                hpss.set_mod_time(mod_time)
        except Exception as ex:
            err_str = "Can't set hpss file mod time with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def set_file_permissions(self):
        """Set the file permissions for an hpss archive file."""
        try:
            if self._filepath:
                hpss = HpssExtended(self._filepath, self._latency)
                hpss.ping_core()
                rcode = self._hpsslib.hpss_Chmod(self._filepath, 0444)
                if rcode < 0:
                    err_str = 'Failed to chmod hpss file with code: ' + \
                        str(rcode)
                    raise ArchiveInterfaceError(err_str)
        except Exception as ex:
            err_str = "Can't set hpss file permissions with error: " + str(ex)
            raise ArchiveInterfaceError(err_str)

    def authenticate(self):
        """Authenticate the user with the hpss system."""
        rcode = self._hpsslib.hpss_SetLoginCred(
            self._user, HPSS_AUTHN_MECH_UNIX,
            HPSS_RPC_CRED_CLIENT, HPSS_RPC_AUTH_TYPE_KEYTAB, self._auth
        )
        if rcode != 0:
            err_str = 'Could Not Authenticate, error code is:' + str(rcode)
            raise ArchiveInterfaceError(err_str)
