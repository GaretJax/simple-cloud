#!/bin/bash

file=/Users/garetjax/Projects/simple-cloud/temp/appliances/server.ova
cores=2
memory=4096
name=server-1
key=/Users/garetjax/Projects/simple-cloud/temp/keys/main.pub

VBoxManage import $file \
	--vsys 0 \
		--vmname $name \
		--cpus $cores \
		--memory $memory

VBoxManage -nologo guestproperty set $name /scloud/hostname $name
VBoxManage -nologo guestproperty set $name /scloud/auth-key "$(cat $key)"
