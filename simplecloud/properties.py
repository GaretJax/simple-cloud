import re
from simplecloud.commands import vboxmanage


PREFIX = '/scloud'
_NOT_PROVIDED = object()


def _key(key):
    if isinstance(key, basestring):
        return PREFIX + '/' + key.strip('/')
    else:
        return PREFIX + '/' + '/'.join(key)


class _VMPropertiesContainer(object):
    def __init__(self, instance, uuid, parent=None, path=()):
        self.instance = instance
        self.uuid = uuid
        self.parent = parent
        self.path = path
        self.data = {}

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self.data.__iter__()

    def __getitem__(self, key):
        if key not in self.data:
            self.data[key] = _VMPropertiesContainer(
                    self.instance, self.uuid, self, self.path + (key,))
        return self.data[key]

    def __contains__(self, key):
        return key in self.data

    def __setitem__(self, key, value):
        # TODO: Check for container data type
        self._populate(key, value)
        set(self.instance, self.uuid, self.path + (key,), value)

    def __delitem__(self, key):
        # TODO: Check for container data type
        del self.data[key]
        unset(self.instance, self.uuid, self.path + (key,))

    def _populate(self, key, value):
        self.data[key] = value


def list(instance, uuid):
    out = vboxmanage(instance, 'guestproperty', 'enumerate', uuid,
            '--patterns', PREFIX + '/*', capture=True)
    props = []

    for line in out.splitlines():
        if line.startswith('Name: '):
            name = line.split(' ', 2)[1][:-1]
            name = name.strip('/').split('/')[1:]
            props.append(tuple(name))

    return props


def set(instance, uuid, key, value):
    return vboxmanage(instance, 'guestproperty', 'set', uuid, _key(key), value)


def get(instance, uuid, key, default=_NOT_PROVIDED):
    val = vboxmanage(instance, 'guestproperty', 'get', uuid, _key(key), capture=True)
    if val.strip() == 'No value set!':
        if default is _NOT_PROVIDED:
            raise KeyError('Property not set')
        else:
            return default
    val = val.strip().split(' ', 1)[1]
    return val


def unset(instance, uuid, key):
    return set(instance, uuid, key, '')


def unset_all(instance, uuid):
    for prop in list(instance, uuid):
        unset(instance, uuid, prop)


def get_all(instance, uuid):
    out = vboxmanage(instance, 'guestproperty', 'enumerate', uuid,
            '--patterns', _key('*'), capture=True)
    lines = []

    for line in out.splitlines():
        if line.startswith('Name: '):
            lines.append(line)
        else:
            lines[-1] += line

    properties = _VMPropertiesContainer(instance, uuid)

    for line in lines:
        m = re.search('Name: (.+), value: (.+), timestamp: (\d+), flags: (.*)', line)
        name, value, timestamp, flags = m.groups()
        propmap = properties
        keys = name.strip('/').split('/')
        for k in keys[1:-1]:
            propmap = propmap[k]
            assert isinstance(propmap, _VMPropertiesContainer)
        propmap._populate(keys[-1], value)

    return properties
