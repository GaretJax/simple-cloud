import os
import glob
import shutil

from subcommands import Command
from subcommands import output


class ResourceAddCommand(Command):
    def __init__(self, manager_class, resname, cmdnames):
        self.manager_class = manager_class
        self.name = cmdnames
        self.resname = resname

    def parser(self):
        parser = self.parser_class()
        parser.add_argument('name', help='Name to be given to the stored {}.'.format(self.resname))
        parser.add_argument('resource', metavar=self.resname, help='Path to the file containing the {} to save.'.format(self.resname))
        return parser

    def execute(self, args):
        manager = self.manager_class(self.config)
        if manager.exists(args.name):
            self.logger.error('{} named \'{}\' already exists'.format(self.resname.capitalize(), args.name))
            return 1
        with open(args.resource, 'rb') as fh:
            manager.add(args.name, fh)
        self.logger.info('{} \'{}\' successfully added.'.format(self.resname.capitalize(), args.name))


class ResourceListCommand(Command):
    def __init__(self, manager_class, resname, cmdnames):
        self.manager_class = manager_class
        self.name = cmdnames
        self.resname = resname

    def execute(self, args):
        manager = self.manager_class(self.config)
        resources = manager.list()

        if resources:
            headers = [manager.resource_class.labels()]
            data = [r._row() for r in resources]
            output.printtable(headers + data, headerrows=1)
        else:
            self.logger.info('No registered {} found.'.format(self.resname))


class ResourceRemoveCommand(Command):
    def __init__(self, manager_class, resname, cmdnames):
        self.manager_class = manager_class
        self.name = cmdnames
        self.resname = resname

    def parser(self):
        parser = self.parser_class()
        parser.add_argument('name', help='Name of the {} to remove.'.format(self.resname))
        return parser

    def execute(self, args):
        manager = self.manager_class(self.config)

        if manager.exists(args.name):
            manager.remove(args.name)
            self.logger.info('{} \'{}\' correctly deleted.'.format(self.resname.capitalize(), args.name))
        else:
            self.logger.warn('{} named \'{}\' not found.'.format(self.resname.capitalize(), args.name))
            return 1


class FilesystemResource(object):

    properties = ('name',)

    def __init__(self, manager, filename):
        self.manager = manager
        self._filename = filename
        self._name = self.manager._name_for_filename(self._filename)

    def filename(self):
        return self._filename

    def name(self):
        return self._name
    name.label = 'Name'

    @classmethod
    def labels(cls):
        return [getattr(cls, n).label for n in cls.properties]

    def _row(self):
        return [getattr(self, n)() for n in self.properties]


class FilesystemResourceManager(object):

    resource_name = '<resource>'
    resource_class = object
    extension = 'res'

    def __init__(self, config):
        self.config = config
        resdir = self.config.get(self.resource_name, 'dirname')
        self.resdir = resdir
        if not os.path.exists(resdir):
            os.makedirs(resdir)

    def _filename_for_name(self, name):
        return os.path.join(self.resdir, name + '.' + self.extension)

    def _name_for_filename(self, path):
        return os.path.basename(path).rsplit('.', 1)[0]

    def exists(self, name):
        return os.path.exists(self._filename_for_name(name))

    def remove(self, name):
        if not self.exists(name):
            raise ValueError('{} \'{}\' not found'.format(
                    self.resource_name.capitalize(), name))
        os.remove(self._filename_for_name(name))

    def get(self, name):
        if not self.exists(name):
            raise ValueError('{} \'{}\' not found'.format(
                    self.resource_name.capitalize(), name))
        return self.resource_class(self, self._filename_for_name(name))

    def list(self):
        res = glob.glob(os.path.join(self.resdir, '*.*'))
        res = (os.path.join(self.resdir, r) for r in res)
        res = (self.resource_class(self, r) for r in res)
        return tuple(res)

    def add(self, name, res):
        if self.exists(name):
            raise ValueError('{} \'{}\' already exists'.format(
                    self.resource_name.capitalize(), name))
        path = self._filename_for_name(name)
        with open(path, 'wb') as fh:
            shutil.copyfileobj(res, fh)
        return self.resource_class(self, path)

    @classmethod
    def make_add_command(cls, *cmdnames):
        return ResourceAddCommand(cls, cls.resource_name, cmdnames)

    @classmethod
    def make_list_command(cls, *cmdnames):
        return ResourceListCommand(cls, cls.resource_name, cmdnames)

    @classmethod
    def make_remove_command(cls, *cmdnames):
        return ResourceRemoveCommand(cls, cls.resource_name, cmdnames)
