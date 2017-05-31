#!/bin/bash -xe

pre-commit run -a
pylint scripts/archiveinterfaceserver.py
pylint archiveinterface.archive_interface
pylint archiveinterface.archive_interface_responses
pylint archiveinterface.archive_interface_error
pylint archiveinterface.archive_utils
pylint archiveinterface.id2filename
pylint archiveinterface.archivebackends.archive_backend_factory
pylint archiveinterface.archivebackends.abstract.abstract_backend_archive
pylint archiveinterface.archivebackends.abstract.abstract_status
pylint archiveinterface.archivebackends.posix.posix_backend_archive
pylint archiveinterface.archivebackends.posix.posix_status
pylint archiveinterface.archivebackends.posix.extendedfile
pylint archiveinterface.archivebackends.hpss.hpss_backend_archive
pylint archiveinterface.archivebackends.hpss.hpss_extended
pylint archiveinterface.archivebackends.hpss.hpss_status
pylint archiveinterface.archivebackends.oracle_hms_sideband.extended_hms_sideband
pylint archiveinterface.archivebackends.oracle_hms_sideband.hms_sideband_backend_archive
pylint archiveinterface.archivebackends.oracle_hms_sideband.hms_sideband_status
pylint archiveinterface.archivebackends.oracle_hms_sideband.hms_sideband_orm