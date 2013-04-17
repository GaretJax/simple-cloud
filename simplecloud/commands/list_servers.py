import re

from simplecloud.commands import Command, vboxmanage

from subcommands import output


class ListServers(Command):
    name = 'servers'
    help = 'Lists currently available servers.'

    def execute(self, args):
        out = vboxmanage(self, 'list', 'vms', capture=True)
        out = out.strip().splitlines()

        vmdata = []

        for line in out:
            name, uuid = line.rsplit(' ', 1)
            name = name[1:-1]
            uuid = uuid[1:-1]

            out = vboxmanage(self, 'showvminfo', name, capture=True)
            info, _ = out.split('\n\n', 1)
            vm = {}

            for line in info.splitlines():
                m = re.search(r'([^:]+):\s+(.*)', line)
                if m:
                    vm[m.group(1).lower()] = m.group(2)
            vmdata.append(vm)


        vmdata = [self.getinfo(vm) for vm in vmdata]
        headers = [
            ('ID', 'Name', 'OS', 'CPU', 'RAM', 'State'),
        ]

        output.printtable(headers + vmdata, headerrows=1)

    def getinfo(self, vm):
        return (
            'srv-' + vm['uuid'][0:6],
            vm['name'], vm['guest os'],
            vm['number of cpus'] + ' Cores',
            vm['memory size'],
            vm['state'].split(' (', 1)[0],
        )

listsrv = ListServers()
