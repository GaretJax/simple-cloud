#!/bin/bash

username=root
ssh_root=/root/.ssh
keysfile=$ssh_root/authorized_keys
property=/scloud/auth-key

# TODO: Add support for multiple keys with different commands (add/remove)


enforce_state() {
	mkdir -p $ssh_root
	chmod 0700 $ssh_root
	chown $username:$username $ssh_root
	touch $keysfile
	chown $username:$username $keysfile
	chmod 0600 $keysfile
}

remove_duplicate_keys() {
	awk '!x[$0]++' $keysfile >$keysfile.tmp && mv $keysfile.tmp $keysfile
}

wait_for_key() {
	VBoxControl -nologo guestproperty wait $property | grep Value: | sed 's/^Value: //' >>$keysfile
}

set_key() {
	VBoxControl -nologo guestproperty get $property | grep Value: | sed 's/^Value: //' >>$keysfile
}


enforce_state
set_key
remove_duplicate_keys

echo "Initial key added, waiting for updates..."
while true
do
	enforce_state
	wait_for_key
	remove_duplicate_keys
	echo "New key received!"
done
