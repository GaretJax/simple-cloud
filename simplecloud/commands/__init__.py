import shlex
import subprocess
import re
import inspect

from subcommands import Command


class VMCommandMixin(object):
    single = False

    def parser(self):
        parser = self.parser_class()
        parser.add_argument(metavar='vm', nargs='+' if not self.single else 1,
            help='UUIDs of the VMs to {}.'.format(self.name), dest='identifiers')
        return parser

    def get_identifiers(self):
        cmd = shlex.split(self.config.get('virtualbox', 'vboxmanage'))
        cmd += [
            'list', 'vms',
        ]
        out = subprocess.check_output(cmd)
        out = out.strip().splitlines()

        matches = (re.search(r'"([^"]+)" \{([0-9a-f-]+)\}', vm) for vm in out)
        matches = ((m.group(2), m.group(1)) for m in matches)

        uuid_to_name = dict(matches)
        name_to_uuid = {v: k for k, v in uuid_to_name.iteritems()}

        return uuid_to_name, name_to_uuid

    def execute(self, args):
        uuids, names = self.get_identifiers()

        for id in args.identifiers:
            if id.startswith('srv-'):
                id = id[4:]

            name = id

            if id not in names:
                name = None
                found = False

                # Check if it is the beginning of a UUID
                for uuid in uuids:
                    if uuid.startswith(id):
                        if found:
                            self.logger.error('Prefix {} yields multiple UUIDs. Identifier ignored.'.format(id))
                            name = None
                            break
                        else:
                            found = True
                            name = uuids[uuid]

                if not found or found and name is None:
                    if not found:
                        self.logger.warn('Invalid UUID {}.'.format(id))
                    self.logger.warn('Known UUIDs are:')
                    for uuid in uuids:
                        self.logger.warn(' * {}'.format(uuid))
                    continue

            self.process_vm(name, names[name], args)

    def process_vm(self, name, uuid, args):
        raise NotImplementedError()


class SimpleVMCommandDecorator(VMCommandMixin, Command):
    def __init__(self, name, help=None, single=False):
        self.name = name
        self.help = help
        self.single = single

    def __call__(self, handler):
        self.handler = handler
        module = inspect.getmodule(handler)
        setattr(module, '_simple_cmd_{}'.format(self.name), self)

    def process_vm(self, name, uuid, args):
        return self.handler(self, name, uuid, args)

vm_callback = SimpleVMCommandDecorator


def vboxmanage(instance, *args, **kwargs):
    capture = kwargs.get('capture', False)
    base = tuple(shlex.split(instance.config.get('virtualbox', 'vboxmanage')))
    if capture:
        return subprocess.check_output(base + args)
    else:
        return subprocess.check_call(base + args)
