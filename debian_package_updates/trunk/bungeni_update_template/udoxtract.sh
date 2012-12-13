#!/bin/bash

mkdir -p previous/data
mkdir -p latest/data
ar p previous/*.deb data.tar.gz | tar zx --directory=previous/data/
ar p latest/*.deb data.tar.gz | tar zx --directory=latest/data/
