#!/bin/bash


machines='salt-master'
devices='virtio-net/0'

name='testzone'
domain='testzone.com'
ip='192.168.56.101'

for m in $machines
do
	for d in $devices
	do
		echo $m $d $domain '->' $ip
		VBoxManage setextradata "$m" "VBoxInternal/Devices/$d/"'LUN#0/Config/HostResolverMappings/'$name'/HostName' $domain
		VBoxManage setextradata "$m" "VBoxInternal/Devices/$d/"'LUN#0/Config/HostResolverMappings/'$name'/HostIP' $ip
	done
done
