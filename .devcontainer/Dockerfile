# استخدام صورة Python رسمية ومستقرة
FROM python:3.12-slim-bookworm

# تثبيت uv من الموقع الرسمي
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# إضافة مسار uv إلى PATH
ENV PATH="/root/.local/bin:$PATH"

# إعدادات uv
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/workspaces/.venv

WORKDIR /workspaces
