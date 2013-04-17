#!/bin/sh

FW=/sbin/iptables

init() {
	# Flush everything
	$FW -F

	# Accept all packets related to previous packets
	$FW -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

	# By default, drop everything
	$FW -P INPUT DROP

	# Accept everything on the loopback device
	$FW -I INPUT -i lo -j ACCEPT
}

finalize() {
	# Save everything
	/etc/init.d/iptables save
}

accept() {
	func=accept_$1
	shift
	$func $@
}

accept_tcp() {
	# Accept ingoing TCP connections on the specified port
	$FW -A INPUT -p tcp --dport $1 -j ACCEPT
}

accept_icmp() {
	$FW -A INPUT -p icmp --icmp-type $1 -j ACCEPT
}

report() {
	# Print rules
	$FW -L -v
}

init
accept tcp ssh
# Open ports 4505, 4506 for the salt master
accept tcp 4505
accept tcp 4506
accept icmp echo-request
report

mkdir -p /srv/salt
mkdir -p /etc/salt
echo "file_roots:"      >/etc/salt/master
echo "  base:"         >>/etc/salt/master
echo "    - /srv/salt" >>/etc/salt/master

echo "Remember to copy you state files to /srv/salt"

rc-update add salt-master default
/etc/init.d/salt-master start
