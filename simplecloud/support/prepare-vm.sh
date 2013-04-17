#!/bin/bash

# How to prepare a disk image
# ---------------------------
#
# On the guest:
#
#    mount -t vboxsf simple-cloud /mnt && cd /mnt/simplecloud/support && ./install-scloud.sh && ./prepare-vm.sh
#    shutdown -h now
#
# On the host (choose the right snapshot):
#
#    VBoxManage clonehd \
#        '/Users/garetjax/VirtualBox VMs/Gentoo Base Box/Snapshots/{06a79d6b-27e9-4860-b166-e536caa0e62e}.vmdk' \
#        /Users/garetjax/Projects/simple-cloud/temp/disks/base.vmdk --format VMDK


echo root:$(< /dev/urandom tr -dc A-Za-z0-9_ | head -c32) | chpasswd
echo " * root password set to 32-digit random value"

/etc/init.d/salt-minion stop 2>/dev/null
/etc/init.d/salt-master stop 2>/dev/null
echo " * salt stopped"

rm -rf /var/run/salt
echo " * salt run information removed"

rm -rf /etc/salt
mkdir -p /etc/salt
echo "master: saltmaster.wsf" >/etc/salt/minion
echo " * salt config reset"

rm -rf ~/.ssh
echo " * root SSH configuration removed"

rm -f /etc/ssh/ssh_host_*_key /etc/ssh/ssh_host_*_key.pub
echo " * host SSH information removed"

/mnt/simplecloud/support/setup-iptables.sh >/dev/null
echo " * firewall rules reset to allow only SSH"

rm -f /etc/udev/rules.d/70-persistent-net.rules
echo " * network cards naming reset"

rm -rf /var/log/*
echo " * log files removed"

rm -rf /tmp/*
echo " * tmp files removed"

rm -f /root/.bash_history
rm -f /root/.lesshst
rm -f /root/.viminfo
echo " * bash, vim and less history removed"

echo " => Ready to SHUTDOWN"
