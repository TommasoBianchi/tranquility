FROM ubuntu:24.04

# Install python
RUN apt update && apt install -y python3

# Install base dependencies
RUN apt install -y git