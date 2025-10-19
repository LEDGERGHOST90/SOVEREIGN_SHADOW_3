# 🏴 Sovereign Shadow Dev Container
# Optimized Python development environment for crypto trading

FROM python:3.11-slim-bullseye

# 📝 Metadata
LABEL maintainer="LEDGERGHOST90"
LABEL description="Sovereign Shadow Trading System - Development Environment"
LABEL version="1.0.0"

# 🔧 Build arguments
ARG USERNAME=trader
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG DEBIAN_FRONTEND=noninteractive

# 🌍 Environment setup
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.0 \
    WORKSPACE=/workspace

# 📦 Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    \
    # Development tools
    git \
    curl \
    wget \
    vim \
    nano \
    \
    # Python development
    python3-dev \
    python3-pip \
    python3-setuptools \
    \
    # Network tools
    net-tools \
    iputils-ping \
    dnsutils \
    telnet \
    netcat \
    \
    # SSL/TLS
    ca-certificates \
    openssl \
    libssl-dev \
    \
    # Database clients
    postgresql-client \
    redis-tools \
    \
    # Data processing libraries
    libpq-dev \
    libhdf5-dev \
    \
    # System utilities
    htop \
    tmux \
    tree \
    jq \
    zip \
    unzip \
    \
    # Shell
    zsh \
    && rm -rf /var/lib/apt/lists/*

# 👤 Create non-root user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && rm -rf /var/lib/apt/lists/*

# 🐍 Upgrade pip and install core Python tools
RUN pip install --upgrade pip setuptools wheel && \
    pip install \
    # Development tools
    ipython \
    jupyter \
    black \
    isort \
    pylint \
    flake8 \
    mypy \
    pytest \
    pytest-cov \
    pytest-asyncio \
    # Debugging
    ipdb \
    pdb++ \
    # Documentation
    sphinx \
    sphinx-rtd-theme

# 📁 Create workspace directory
RUN mkdir -p $WORKSPACE && chown -R $USERNAME:$USERNAME $WORKSPACE

# 👤 Switch to non-root user
USER $USERNAME
WORKDIR $WORKSPACE

# 🎨 Configure shell (zsh with Oh My Zsh is added via devcontainer feature)
RUN echo 'export PYTHONPATH="$WORKSPACE:$PYTHONPATH"' >> ~/.bashrc && \
    echo 'export WORKSPACE=/workspace' >> ~/.bashrc && \
    echo 'alias python=python3' >> ~/.bashrc && \
    echo 'alias pip=pip3' >> ~/.bashrc

# 📝 Set default command
CMD ["/bin/zsh"]

