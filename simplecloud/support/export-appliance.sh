#!/bin/bash

machines=$1
output=$2

get_properties() {
	VBoxManage guestproperty enumerate $1 | grep -oE '^Name: /scloud[^,]+' | cut -f 2 -d ' '
}

clear_properties() {
	for p in $(get_properties $1)
	do
		VBoxManage guestproperty set $1 $p
	done
}

for m in $machines
do
	clear_properties $m
done

mkdir -p $(dirname $output)

VBoxManage export $machines -o $output --manifest \
	--vsys 0 \
	--product 'simple-cloud Gentoo 3.7.10 Base VM + salt' \
	--vendor 'Watersports Fashion Company Ltd.' \
	--version '1.0rc2'
