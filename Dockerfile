FROM ubuntu:20.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libgdbm-dev \
    libdb5.3-dev \
    libbz2-dev \
    libexpat1-dev \
    liblzma-dev \
    tk-dev \
    libffi-dev \
    libgdbm-compat-dev

# Install Python 3.12.1
RUN wget https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tgz \
    && tar xzf Python-3.12.1.tgz \
    && cd Python-3.12.1 \
    && ./configure --enable-optimizations \
    && make altinstall

# Set up Python environment
RUN python3.12 -m venv /opt/pythonenv
ENV PATH="/opt/pythonenv/bin:$PATH"

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* Python-3.12.1.tgz Python-3.12.1
