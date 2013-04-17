#!/bin/bash

if [ -z $1 ]
then
	build=""
else
	build="-$1"
fi

cd /usr/src/linux
version=$(make kernelversion)

if [ ! -d "/boot/grub" ]; then
	mount /dev/sda1 /boot
fi
cp arch/x86/boot/bzImage /boot/kernel-$version$build

# grep -v rootfs /proc/mounts > /etc/mtab
# grub-install --no-floppy /dev/sda
