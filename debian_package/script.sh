#!/bin/bash
set -x verbose
# install required libraries
# THIS IS FOR UBUNTU 12.04 
apt-get install build-essential ssh subversion python-dev python-setuptools fabric wget zip unzip build-essential libjpeg62-dev libfreetype6-dev libbz2-dev libxslt1-dev libxml2-dev libpng12-dev openssl libssl-dev bison flex libreadline-dev zlib1g-dev libtool automake autoconf libsqlite3-dev uuid-dev libreoffice-writer libreoffice-java-common libreoffice-common python-uno libtidy-dev libldap2-dev libsasl2-dev libssl-dev wv poppler-utils libdb-dev libpq-dev erlang-base-hipe erlang-os-mon erlang-xmerl erlang-inets openjdk-7-jre -Y
# add bungeni user
useradd bungeni
# generate default password for bungeni user
echo bungeni:bungeni | sudo chpasswd
# create & set home directory for bungeni user
mkdir -p /opt/bungeni
chown -R bungeni:bungeni /opt/bungeni
usermod -d /opt/bungeni bungeni
# extract bungeni installation 
tar xvf bungeni.tar.gz --directory=/opt/bungeni

