FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# إنشاء مستخدم vscode بمعرّف ثابت 1000 لتجنب مشاكل الصلاحيات
RUN apt-get update \
    && apt-get install -y --no-install-recommends passwd sudo \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash -u 1000 vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# إعدادات uv
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/workspaces/.venv

# إنشاء مجلد العمل وتمليكه للمستخدم vscode
WORKDIR /workspaces
RUN chown vscode:vscode /workspaces

USER vscode
