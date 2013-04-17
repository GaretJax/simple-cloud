import re
import subprocess

from subcommands import output

from simplecloud import images, keys, properties
from simplecloud.commands import Command, vm_callback, vboxmanage


class Presets(Command):
    name = 'types'
    prefix = 'preset-'

    def execute(self, args):
        headers = ((
            'Name', 'Cores', 'RAM [MB]'
        ),)

        data = self.config.sections()
        data = (s for s in data if s.startswith(self.prefix))
        data = ((
            s[len(self.prefix):],
            self.config.get(s, 'cores'),
            self.config.get(s, 'memory'),
        ) for s in data)

        output.printtable(headers + tuple(data), headerrows=1)

presets = Presets()


class CreateServer(Command):
    name = 'create'

    def parser(self):
        parser = self.parser_class()
        parser.add_argument('name')
        parser.add_argument('image')
        parser.add_argument('type')
        parser.add_argument('key')
        return parser

    def execute(self, args):
        image = images.Manager(self.config).get(args.image)
        key = keys.Manager(self.config).get(args.key)
        preset = dict(self.config.items(Presets.prefix + args.type))
        name = args.name.replace(' ', '-')

        vboxmanage(self, 'import', image.filename(),
            '--vsys', '0',
            '--vmname', name,
            '--cpus', preset['cores'],
            '--memory', preset['memory']
        )

        properties.set(self, name, 'auth-key', key.content())

        # TODO: Set network adapters configuration
        # TODO: Set DNS proxy configuration
        # TODO: Disable vrde console

create = CreateServer()

# TODO: Make a recover command which boots from a simple recovery CD

@vm_callback('info', 'Retrieve information about the selected VMs.')
def info_vm(instance, name, uuid, args):
    output.printtree(properties.get_all(instance, uuid))


@vm_callback('shell', 'Opens an SSH shell to the selected VM', single=True)
def shell_vm(instance, name, uuid, args):
    iface = instance.config.get('networking', 'shell_iface')
    ip = properties.get(instance, uuid, ('iface', iface, 'ipv4'))
    user = 'root'
    connection_string = '{}@{}'.format(user, ip)
    cmd = [
        'ssh',
        connection_string,
    ]
    if not instance.config.getboolean('shell', 'check_keys'):
        cmd += [
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
        ]

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        code = e.returncode
        instance.logger.warn('Shell terminated with exit code {}'.format(code))


@vm_callback('destroy', 'Destroys the selected VMs.')
def destroy_vm(instance, name, uuid, args):
    vboxmanage(instance, 'unregistervm', '--delete', uuid)


@vm_callback('start', 'Starts the selected VMs.')
def start_vm(instance, name, uuid, args):
    vboxmanage(instance, 'guestproperty', 'set', uuid,
            '/scloud/hostname', name)
    vboxmanage(instance, 'startvm', uuid, '--type', 'headless')


@vm_callback('save', 'Saves the selected VMs states.')
def save_vm(instance, name, uuid, args):
    vboxmanage(instance, 'controlvm', uuid, 'savestate')


@vm_callback('stop', 'Instantly remove power from the selected VMs.')
def stop_vm(instance, name, uuid, args):
    vboxmanage(instance, 'controlvm', uuid, 'poweroff')


@vm_callback('reset', 'Hard-reboots the selected VMs.')
def reset_vm(instance, name, uuid, args):
    vboxmanage(instance, 'controlvm', uuid, 'reset')


@vm_callback('pause', 'Pauses the selected VMs.')
def pause_vm(instance, name, uuid, args):
    vboxmanage(instance, 'controlvm', uuid, 'pause')


@vm_callback('resume', 'Resumes the selected VMs.')
def resume_vm(instance, name, uuid, args):
    vboxmanage(instance, 'controlvm', uuid, 'resume')
