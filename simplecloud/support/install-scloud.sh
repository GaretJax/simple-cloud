#!/bin/bash

base=/mnt/simplecloud

# Install authkey updater
cp $base/support/authkeys-updater.sh /usr/local/bin/authkeys-updater
echo " * installed authekys updater script to /usr/local/bin"

cp $base/support/authkeys-init.sh /etc/init.d/authkeys
echo " * installed authekys init script "

conf=/etc/conf.d/authekys
rm -f $conf
echo "daemon=/usr/local/bin/authkeys-updater" >$conf
echo "pidfile=/run/authkeys-updater.pid"     >>$conf
echo "logfile=/var/log/authkeys-updater"     >>$conf
echo " * config file for authkeys daemon created"

rc-update add authkeys default

# Install hostname updater
echo 'hostname=$(VBoxControl -nologo guestproperty get /scloud/hostname | grep Value: | sed "s/^Value: //")' >/etc/conf.d/hostname
echo " * hostname config script updated"

# Install IP writer
rc-update add local default

cp $base/support/write-ips.sh /usr/local/bin/write-ips
ln -fs /usr/local/bin/write-ips /etc/local.d/20-write-ips.start
echo " * write-ips script added to local.d"

(crontab -l ; echo "10 * * * * /usr/local/bin/write-ips") | awk 'substr($1, 0, 1) != "#" && !x[$0]++' | crontab -
echo " * write-ips script scheduled to run each 10 minutes"

# Setup salt to run on boot
rc-update add salt-minion default
