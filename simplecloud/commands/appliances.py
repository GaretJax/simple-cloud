import os

from simplecloud import properties
from simplecloud.commands import VMCommandMixin, Command, vboxmanage


class Export(VMCommandMixin, Command):
    name = 'export'
    single = True

    def parser(self):
        parser = super(Export, self).parser()
        parser.add_argument('dest')
        parser.add_argument('-f', '--force', default=False, action='store_true')
        return parser

    def process_vm(self, name, uuid, args):
        if not os.path.exists(os.path.dirname(args.dest)):
            os.makedirs(os.path.dirname(args.dest))

        properties.unset_all(self, uuid)

        if os.path.exists(args.dest):
            if args.force:
                self.logger.info('Removing existing file at \'{}\''.format(args.dest))
                os.remove(args.dest)
            else:
                self.logger.error('Destination already exists (use -f/--force to override)')
                return


        vboxmanage(self, 'export', uuid, '-o', args.dest, '--manifest',
            '--vsys', '0',
                # TODO: Make the following values optional or coming from
                #       the configuration/command line arguments.
                '--product', 'simple-cloud Gentoo 3.7.10 Base VM + salt',
                '--vendor', 'Watersports Fashion Company Ltd.',
                '--version', '1.0rc2',
        )

kset = Export()
