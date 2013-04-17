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
	port=$1
	shift
	$FW -A INPUT -p tcp --dport $port $@ -j ACCEPT
}

accept_udp() {
	# Accept ingoing TCP connections on the specified port
	port=$1
	shift
	$FW -A INPUT -p udp --dport $port $@ -j ACCEPT
}

accept_icmp() {
	port=$1
	shift
	$FW -A INPUT -p icmp --icmp-type $port $@ -j ACCEPT
}

report() {
	# Print rules
	$FW -L -v
}

init
accept tcp ssh
accept icmp echo-request
accept udp ntp
accept udp bootps
accept udp bootpc

# Allow DNS replies
accept tcp 1024:65535 --sport dns
accept udp 1024:65535 --sport dns

report
