#!/bin/bash

###
### This integration test tries to install this repository with
### "pip install ." command. It doesn't produce any artifacts.
### Necessary packages/utilities/services:
###   bash
###   bsdmainutils
###   docker
###

###
### Config
###
IMAGE="python:3.11"

###
### Detect repo root
###
REPOROOT="$(pwd)"
if ls -1 .git/config &>/dev/null; then
    REPOROOT="."
else
    if ls -1 ../.git/config &>/dev/null; then
    REPOROOT=".."
    else
        if ls -1 ../.git/config &>/dev/null; then
        REPOROOT="../.."
        else
            echo "Please switch to the root folder of the repository and try again" 1>&2
            exit 1
        fi
    fi
fi
REPOROOT="$(realpath "${REPOROOT}")"

###
### Check package install
###
set -e
docker run --rm -i \
    --volume "${REPOROOT}:/app:rw" \
    --workdir /app \
    "${IMAGE}" \
        bash -ec "pip install . && cd / &>/dev/null && rofehcloud -v"
set +e

###
### Check devepment mode
###
set -e
docker run --rm -i \
    --volume "${REPOROOT}:/app:rw" \
    --workdir /app \
    "${IMAGE}" \
        bash -ec "pip install -r requirements.txt && python ./src/rofehcloud/__main__.py -v"
set +e
