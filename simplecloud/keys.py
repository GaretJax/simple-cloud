import base64
import hashlib

from simplecloud import resources


class Key(resources.FilesystemResource):

    properties = ('name', 'fingerprint')

    def fingerprint(self):
        key = self.content().strip().split('ssh-rsa ', 1)[1]
        key = base64.b64decode(key)
        hashed = hashlib.md5(key).hexdigest()
        return ':'.join(a + b for a, b in zip(hashed[::2], hashed[1::2]))
    fingerprint.label = 'Fingerprint'

    def content(self):
        with open(self._filename, 'rb') as fh:
            content = fh.read()
        return content



class Manager(resources.FilesystemResourceManager):
    resource_class = Key
    resource_name = 'key'
    extension = 'pub'
