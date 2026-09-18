FROM python:3.13-bookworm
ARG DCC_ENV=dev
# Optimise python and debian in docker
ENV PYTHONUNBUFFERED 1
ENV PIP_BREAK_SYSTEM_PACKAGES 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV DEBIAN_FRONTEND noninteractive

# Create the required directories
RUN mkdir -p /app
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN mkdir -p /vol/backups

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg graphviz libgraphviz-dev && \
    curl -fsSL https://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client-18 && \
    pip install --no-cache-dir pygraphviz && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Update pip
RUN pip install --upgrade pip

# Global python requirements
COPY ./requirements.dev.txt /
COPY ./requirements.txt /

RUN if [ "$DCC_ENV" = "dev" ]; then \
    pip install -r /requirements.dev.txt; \
else \
    pip install -r /requirements.txt; \
fi

# Set working directory
WORKDIR /app
