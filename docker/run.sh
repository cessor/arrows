#!/bin/bash
docker run --name mongodb -v $(pwd)/data:/data/db -d mongo:latest
docker run --name arrows -d -p 8000:8000 --link mongodb:mongodb cessor/arrows
