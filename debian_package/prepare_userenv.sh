#!/bin/bash
set -x verbose
# add bungeni user
useradd bungeni
# generate default password for bungeni user
echo bungeni:bungeni | sudo chpasswd
# create & set home directory for bungeni user
mkdir -p /opt/bungeni
chown -R bungeni:bungeni /opt/bungeni
usermod -d /opt/bungeni bungeni

