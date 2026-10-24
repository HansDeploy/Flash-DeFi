FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Create the vscode user with a fixed ID of 1000 to avoid permission issues.
RUN apt-get update \
    && apt-get install -y --no-install-recommends passwd sudo \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash -u 1000 vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# uv settings
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/workspaces/.venv

# Create the workspace directory and assign ownership to vscode.
WORKDIR /workspaces
RUN chown vscode:vscode /workspaces

USER vscode
