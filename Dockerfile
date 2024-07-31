FROM ubuntu:24.04

# Install python
RUN apt update && apt install -y python3 python3-venv

# Install base dependencies
RUN apt install -y git curl

USER ubuntu

# Install package manager (PDM)
RUN curl -sSL https://pdm-project.org/install-pdm.py | python3 -
ENV PATH=/home/ubuntu/.local/bin:$PATH

# Install formatter and linter (Ruff)
RUN curl -LsSf https://astral.sh/ruff/install.sh | sh
