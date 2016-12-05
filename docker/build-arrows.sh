#!/bin/bash
docker pull mongo
docker build -t cessor/arrows -f Dockerfile ..