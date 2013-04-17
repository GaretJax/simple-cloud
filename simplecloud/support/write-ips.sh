#!/bin/bash


get_ipv4() {
	ifconfig $1 | grep -oE 'inet ([0-9]{1,3}\.){3}[0-9]{1,3}' | awk '{print $2}'
}

get_mac() {
	ifconfig $1 | grep -oE 'ether ([0-9a-z]{2}:){5}[0-9a-z]{2}' | awk '{print $2}'
}

get_interfaces() {
	ifconfig -s | awk 'NR>1{print $1}'
}

get_ipname() {
	echo /scloud/iface/$1/ipv4
}

get_macname() {
	echo /scloud/iface/$1/hw
}

write_ip() {
	VBoxControl -nologo guestproperty set $(get_ipname $1) $2
}

write_mac() {
	VBoxControl -nologo guestproperty set $(get_macname $1) $2
}


for i in $(get_interfaces)
do
	write_ip $i $(get_ipv4 $i)
	write_mac $i $(get_mac $i)
done


# On the host, information can be retrieved by running
# VBoxManage guestproperty enumerate <name|uuid> --patterns '/scloud/iface/*/ipv4'
