FROM ubuntu:24.04

# Install python
RUN apt update && apt install -y python3 python3-venv

# Install base dependencies
RUN apt install -y git curl

# Install package manager (PDM)
RUN curl -sSL https://pdm-project.org/install-pdm.py | python3 -
ENV PATH=/root/.local/bin:$PATH
