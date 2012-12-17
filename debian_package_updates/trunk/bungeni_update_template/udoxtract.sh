#!/bin/bash

mkdir -p previous/ctrl
mkdir -p latest/ctrl

mkdir -p previous/data
mkdir -p latest/data

ar p previous/*.deb control.tar.gz | tar zx --directory=previous/ctrl
ar p latest/*.deb control.tar.gz | tar zx --directory=latest/ctrl

ar p previous/*.deb data.tar.gz | tar vzx --directory=previous/data/ > previous/ctrl/list
ar p latest/*.deb data.tar.gz | tar vzx --directory=latest/data/ > latest/ctrl/list

sed -i 's/\.\//\//g' previous/ctrl/list
sed -i 's/\.\//\//g' latest/ctrl/list
