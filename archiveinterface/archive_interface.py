#!/usr/bin/python
"""Class for the archive interface.

Allows API to file interactions for passed in archive backends.
"""
import json
from sys import stderr
from archiveinterface.archive_utils import get_http_modified_time
from archiveinterface.archive_interface_error import ArchiveInterfaceError
import archiveinterface.archive_interface_responses as interface_responses

BLOCK_SIZE = 1 << 20


class ArchiveInterfaceGenerator(object):
    """Archive Interface Generator.

    Defines the methods that can be used on files for request types.
    """

    def __init__(self, archive):
        """Create an archive interface generator."""
        self._archive = archive
        self._response = None
        print 'Pacifica Archive Interface Up and Running'

    def get(self, env, start_response):
        """Get a file from WSGI request.

        Gets a file specified in the request and writes back the data.
        """
        archivefile = None
        path_info = env['PATH_INFO']
        # if asking for / then return a message that the archive is working
        if path_info == '/':
            resp = interface_responses.Responses()
            self._response = resp.archive_working_response(start_response)
            return self.return_response()
        stderr.flush()
        archivefile = self._archive.open(path_info, 'r')

        start_response('200 OK', [('Content-Type',
                                   'application/octet-stream')])
        if 'wsgi.file_wrapper' in env:
            return env['wsgi.file_wrapper'](archivefile, BLOCK_SIZE)
        return iter(lambda: archivefile.read(BLOCK_SIZE), '')

    def put(self, env, start_response):
        """Write a file from WSGI requests.

        Writes a file passed in the request to the archive.
        """
        archivefile = None
        resp = interface_responses.Responses()
        path_info = env['PATH_INFO']
        mod_time = get_http_modified_time(env)
        stderr.flush()
        archivefile = self._archive.open(path_info, 'w')
        try:
            content_length = int(env['CONTENT_LENGTH'])
        except Exception as ex:
            raise ArchiveInterfaceError(
                "Can't get file content length with error: {}".format(str(ex))
            )
        while content_length > 0:
            if content_length > BLOCK_SIZE:
                buf = env['wsgi.input'].read(BLOCK_SIZE)
            else:
                buf = env['wsgi.input'].read(content_length)
            archivefile.write(buf)
            content_length -= len(buf)

        self._response = resp.successful_put_response(start_response,
                                                      env['CONTENT_LENGTH'])
        archivefile.close()
        archivefile.set_mod_time(mod_time)
        archivefile.set_file_permissions()
        return self.return_response()

    def status(self, env, start_response):
        """Get the file status from WSGI request.

        Gets the status of a file specified in the request.
        """
        archivefile = None
        path_info = env['PATH_INFO']
        resp = interface_responses.Responses()
        stderr.flush()
        archivefile = self._archive.open(path_info, 'r')
        status = archivefile.status()
        self._response = resp.file_status(start_response, status)
        archivefile.close()
        return self.return_response()

    def stage(self, env, start_response):
        """Stage a file from WSGI request.

        Stage the file specified in the request to disk.
        """
        archivefile = None
        path_info = env['PATH_INFO']
        resp = interface_responses.Responses()
        stderr.flush()
        archivefile = self._archive.open(path_info, 'r')
        archivefile.stage()
        self._response = resp.file_stage(start_response, path_info)
        archivefile.close()
        return self.return_response()

    def patch(self, env, start_response):
        """Move a file from the original path to the new one specified
        """
        archivefile = None
        resp = interface_responses.Responses()
        try:
            request_body_size = int(env.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0

        try:
            request_body = env['wsgi.input'].read(request_body_size)
            data = json.loads(request_body)
            file_path = data['path']
            file_id = env['PATH_INFO']
        except IOError:
            # is exception is probably from the read()
            self._response = resp.json_patch_error_response(start_response)
            return self.return_response()
        except ValueError:
            self._response = resp.json_patch_error_response(start_response)
            return self.return_response()
        stderr.flush()
        patch = self._archive.patch(file_id, file_path)
        self._response = resp.file_patch(start_response, patch)
        return self.return_response()

    def return_response(self):
        """Print all responses in a nice fashion."""
        return json.dumps(self._response, sort_keys=True, indent=4)

    def pacifica_archiveinterface(self, env, start_response):
        """Parse request method type."""
        try:
            if env['REQUEST_METHOD'] == 'GET':
                return self.get(env, start_response)
            elif env['REQUEST_METHOD'] == 'PUT':
                return self.put(env, start_response)
            elif env['REQUEST_METHOD'] == 'HEAD':
                return self.status(env, start_response)
            elif env['REQUEST_METHOD'] == 'POST':
                return self.stage(env, start_response)
            elif env['REQUEST_METHOD'] == 'PATCH':
                return self.patch(env, start_response)
            resp = interface_responses.Responses()
            self._response = resp.unknown_request(start_response,
                                                  env['REQUEST_METHOD'])
            return self.return_response()
        except ArchiveInterfaceError as ex:
            # catching application errors
            # set the error reponse
            resp = interface_responses.Responses()
            self._response = resp.archive_exception(start_response, ex, env['REQUEST_METHOD'])
            return self.return_response()


if __name__ == '__main__':
    pass
