from simplecloud import keys, properties
from simplecloud.commands import VMCommandMixin, Command

add = keys.Manager.make_add_command('keyadd')
ls = keys.Manager.make_list_command('keys')
rm = keys.Manager.make_remove_command('keyrm')


class KeySet(VMCommandMixin, Command):
    name = 'keyset'
    single = False

    def parser(self):
        parser = self.parser_class()
        parser.add_argument('key')
        parser.add_argument(metavar='vm', nargs='+' if not self.single else 1,
            help='UUIDs of the VMs to {}.'.format(self.name), dest='identifiers')
        return parser

    def process_vm(self, name, uuid, args):
        manager = keys.Manager(self.config)
        key = manager.get(args.key)
        properties.set(self, uuid, 'auth-key', key.content())

kset = KeySet()
