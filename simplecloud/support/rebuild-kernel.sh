#!/bin/bash

cd /usr/src/linux
make menuconfig && make -j5
