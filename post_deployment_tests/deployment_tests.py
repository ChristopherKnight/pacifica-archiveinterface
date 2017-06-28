import os
import json
import requests
import unittest

#url for the archive interface just deployed.
ARCHIVEURL = 'http://127.0.0.1:8080/'
CLEANLOCALFILES = True
CLEANARCHIVEFILES = True
ARCHIVEPREFIX = '/home/knig880/archive/'


class BasicArchiveTests(unittest.TestCase):
    local_files = {}
    archive_files = {}
    def test_simple_write(self):
        filename = '/tmp/test_simple_write.txt'
        fileid = '1234'
        file1 = open(filename,'w+')
        file1.write('Writing content for first file')
        file1.close()
        self.local_files[filename] = filename
        filesize = os.path.getsize(filename)
        f = open(filename,'rb')
        resp = requests.put(str(ARCHIVEURL + fileid), data=f)
        f.close()
        self.assertEqual(resp.status_code, 201)
        self.archive_files[fileid] = fileid
        data = resp.json()
        self.assertEqual(int(data['total_bytes']), 30)
        self.assertEqual(data['message'], 'File added to archive')

    def test_simple_status(self):
        fileid = '1234'
        resp = requests.head(str(ARCHIVEURL + fileid))
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(resp.headers['x-pacifica-file-storage-media'], 'disk')
        self.assertEqual(resp.headers['content-length'], '30')
        self.assertEqual(resp.headers['x-pacifica-messsage'], 'File was found')

    def test_simple_stage(self):
        fileid = '1234'
        resp = requests.post(str(ARCHIVEURL + fileid))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['message'], 'File was staged')

    def test_simple_read(self):
        fileid = '1234'
        filename = '/tmp/test_simple_read.txt'
        resp = requests.get(str(ARCHIVEURL + fileid), stream=True)
        myfile = open(filename, 'wb+')
        buf = resp.raw.read(1024)
        while buf:
            myfile.write(buf)
            buf = resp.raw.read(1024)
        myfile.close()
        filesize = os.path.getsize(filename)
        #know the simple file writtten is 30 bytes from archive
        self.assertEqual(filesize, 30)

    def test_file_rewrite(self):
        """Test trying to rewrite a file, rewrite should fail"""
        filename = '/tmp/test_simple_write.txt'
        fileid = '1234'
        file1 = open(filename,'w+')
        file1.write('Writing content for first file')
        file1.close()
        filesize = os.path.getsize(filename)
        f = open(filename,'rb')
        resp = requests.put(str(ARCHIVEURL + fileid), data=f)
        f.close()
        self.assertEqual(resp.status_code, 500)
        data = resp.json()
        error_msg = "Can't open"
        #get error message length since the file path returned is unique per deploymnet while
        #the rest of the error message is not
        err_msg_length = len(error_msg)
        self.assertEqual(data['message'][:err_msg_length], error_msg)

class BinaryFileArchiveTests(unittest.TestCase):
    def test_binary_file_write(self):
        filename = '/tmp/binary_file'
        fileid = '4321'
        newFileBytes = [123, 3, 255, 0, 100]
        file1 = open(filename,'wb+')
        newFileByteArray = bytearray(newFileBytes)
        file1.write(newFileByteArray)
        file1.close()
        filesize = os.path.getsize(filename)
        f = open(filename,'rb')
        resp = requests.put(str(ARCHIVEURL + fileid), data=f)
        f.close()
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(int(data['total_bytes']), 5)
        self.assertEqual(data['message'], 'File added to archive')

    def test_binary_file_status(self):
        fileid = '4321'
        resp = requests.head(str(ARCHIVEURL + fileid))
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(resp.headers['x-pacifica-file-storage-media'], 'disk')
        self.assertEqual(resp.headers['content-length'], '5')
        self.assertEqual(resp.headers['x-pacifica-messsage'], 'File was found')

    def test_binary_file_stage(self):
        fileid = '4321'
        resp = requests.post(str(ARCHIVEURL + fileid))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['message'], 'File was staged')

    def test_binary_file_read(self):
        fileid = '4321'
        filename = '/tmp/test_binary_read'
        resp = requests.get(str(ARCHIVEURL + fileid), stream=True)
        myfile = open(filename, 'wb+')
        buf = resp.raw.read(1024)
        while buf:
            myfile.write(buf)
            buf = resp.raw.read(1024)
        myfile.close()
        filesize = os.path.getsize(filename)
        #know the simple file writtten is 30 bytes from archive
        self.assertEqual(filesize, 5)

    def test_binary_file_rewrite(self):
        """Test trying to rewrite a file, rewrite should fail"""
        filename = '/tmp/binary_file'
        fileid = '4321'
        newFileBytes = [123, 3, 255, 0, 100]
        file1 = open(filename,'wb+')
        newFileByteArray = bytearray(newFileBytes)
        file1.write(newFileByteArray)
        file1.close()
        filesize = os.path.getsize(filename)
        f = open(filename,'rb')
        resp = requests.put(str(ARCHIVEURL + fileid), data=f)
        f.close()
        self.assertEqual(resp.status_code, 500)
        data = resp.json()
        error_msg = "Can't open"
        #get error message length since the file path returned is unique per deploymnet while
        #the rest of the error message is not
        err_msg_length = len(error_msg)
        self.assertEqual(data['message'][:err_msg_length], error_msg)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(BasicArchiveTests('test_simple_write'))
    suite.addTest(BasicArchiveTests('test_simple_status'))
    suite.addTest(BasicArchiveTests('test_simple_stage'))
    suite.addTest(BasicArchiveTests('test_simple_read'))
    suite.addTest(BasicArchiveTests('test_file_rewrite'))
    suite.addTest(BinaryFileArchiveTests('test_binary_file_write'))
    suite.addTest(BinaryFileArchiveTests('test_binary_file_status'))
    suite.addTest(BinaryFileArchiveTests('test_binary_file_stage'))
    suite.addTest(BinaryFileArchiveTests('test_binary_file_read'))
    suite.addTest(BinaryFileArchiveTests('test_binary_file_rewrite'))
    return suite

if __name__ == "__main__":
    #trigger the test suite
    runner = unittest.TextTestRunner()
    runner.run(suite())