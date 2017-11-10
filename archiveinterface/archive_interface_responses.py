#!/usr/bin/python
"""Archive interface server responses module."""


class Responses(object):
    """Class to support the archive interface responses."""

    def __init__(self):
        """Constructor for the responses object."""
        self._response = None

    def unknown_request(self, start_response, request_method):
        """Response for when unknown request type given."""
        start_response(
            '400 Bad Request',
            [('Content-Type', 'application/json')]
        )
        self._response = {
            'message': 'Unknown request method',
            'request_method': request_method
        }
        return self._response

    def unknown_exception(self, start_response):
        """Response when unknown exception occurs."""
        start_response(
            '500 Internal Server Error',
            [('Content-Type', 'application/json')]
        )
        self._response = {
            'message': 'Unknown Exception Occured'
        }
        return self._response

    def successful_put_response(self, start_response, total_bytes):
        """Response on a successful put."""
        start_response('201 Created', [('Content-Type', 'application/json')])
        self._response = {
            'message': 'File added to archive',
            'total_bytes': total_bytes
        }
        return self._response

    def file_patch(self, start_response, test):
        """Response on a successful put."""
        start_response('200 OK', [('Content-Type', 'application/json')])
        self._response = {
            'message': 'File being patched,
            'filepath': test
        }
        return self._response

    def archive_working_response(self, start_response):
        """Response when doing a get on /."""
        start_response('200 OK', [('Content-Type', 'application/json')])
        self._response = {
            'message': 'Pacifica Archive Interface Up and Running'
        }
        return self._response

    def file_stage(self, start_response, filename):
        """Response for when file is on the hpss system."""
        start_response('200 OK', [('Content-Type', 'application/json')])
        self._response = {
            'message': 'File was staged',
            'file': str(filename)
        }
        return self._response

    def file_status(self, start_response, status):
        """Response for when file is on the hpss system."""
        self._response = ''
        if status:
            response_headers = [
                ('X-Pacifica-Messsage', 'File was found'),
                ('X-Pacifica-File', str(status.filepath)),
                ('Content-Length', str(status.filesize)),
                ('Last-Modified', str(status.mtime)),
                ('X-Pacifica-Ctime', str(status.ctime)),
                ('X-Pacifica-Bytes-Per-Level', str(status.bytes_per_level)),
                ('X-Pacifica-File-Storage-Media', str(status.file_storage_media)),
                ('Content-Type', 'application/json')
            ]
            start_response('204 No Content', response_headers)
        else:
            response_headers = [
                ('X-Pacifica-Messsage', 'File Not found'),
                ('X-Pacifica-File', 'File Not Found'),
                ('Content-Length', 'File Not Found'),
                ('Last-Modified', 'File Not Found'),
                ('X-Pacifica-Ctime', 'File Not Found'),
                ('X-Pacifica-Bytes-Per-Level', 'File Not Found'),
                ('X-Pacifica-File-Storage-Media', 'File Not Found'),
                ('Content-Type', 'application/json')
            ]
            start_response('404 Not Found', response_headers)
        return self._response

    def archive_exception(self, start_response, ex, request_method=None):
        """Response when unknown exception occurs."""
        if request_method == 'HEAD':
            response_headers = [
                ('X-Pacifica-Messsage', 'Error: ' + str(ex)),
                ('X-Pacifica-File', 'Error'),
                ('Content-Length', 'Error'),
                ('Last-Modified', 'Error'),
                ('X-Pacifica-Ctime', 'Error'),
                ('X-Pacifica-Bytes-Per-Level', 'Error'),
                ('X-Pacifica-File-Storage-Media', 'Error'),
                ('Content-Type', 'application/json')
            ]
            start_response('500 Internal Server Error', response_headers)
        else:
            start_response(
                '500 Internal Server Error',
                [('Content-Type', 'application/json')]
            )
            self._response = {
                'message': str(ex)
            }
        return self._response
