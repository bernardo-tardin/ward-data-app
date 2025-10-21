FROM python:3.11-slim as builder

ARG DB_TYPE=oracle

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install build-time dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    python3-dev \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libffi-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    libssl-dev \
    libpq-dev \
    unixodbc-dev \
    wget \
    unzip \
    curl \
    gnupg \
    debian-archive-keyring \
    && rm -rf /var/lib/apt/lists/*

# Install Oracle client if DB_TYPE is oracle
RUN if [ "$DB_TYPE" = "oracle" ]; then \
    echo "--- Installing Oracle client ---" && \
    wget http://ftp.debian.org/debian/pool/main/liba/libaio/libaio1_0.3.113-4_amd64.deb && \
    dpkg -i libaio1_0.3.113-4_amd64.deb && \
    rm libaio1_0.3.113-4_amd64.deb && \
    mkdir -p /opt/oracle && \
    wget --no-cookies --no-check-certificate \
    --header "Cookie: oraclelicense=accept-securebackup-cookie" \
    https://download.oracle.com/otn_software/linux/instantclient/193000/instantclient-basic-linux.x64-19.3.0.0.0dbru.zip -O instantclient-basic-linux.zip && \
    unzip instantclient-basic-linux.zip && \
    mv instantclient_19_3 /opt/oracle/ && \
    rm -f instantclient-basic-linux.zip; \
    fi

WORKDIR /app
COPY requirements.txt .
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- Final runtime stage ---
FROM python:3.11-slim

ARG DB_TYPE=oracle
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libjpeg62-turbo \
    libxml2 \
    libxslt1.1 \
    libpq5 \
    netcat-openbsd \
    shared-mime-info \
    unixodbc \
    && rm -rf /var/lib/apt/lists/*

# Copy Oracle client from builder
COPY --from=builder /opt/oracle /opt/oracle
RUN if [ "$DB_TYPE" = "oracle" ]; then \
    echo "--- Configuring Oracle runtime ---" && \
    apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    wget http://ftp.debian.org/debian/pool/main/liba/libaio/libaio1_0.3.113-4_amd64.deb && \
    dpkg -i libaio1_0.3.113-4_amd64.deb && \
    rm libaio1_0.3.113-4_amd64.deb && \
    apt-get purge -y --auto-remove wget && \
    rm -rf /var/lib/apt/lists/*; \
    fi
ENV ORACLE_HOME=/opt/oracle/instantclient_19_3
ENV LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
ENV PATH=$ORACLE_HOME:$PATH

# Install SQL Server client if DB_TYPE is sqlserver
RUN if [ "$DB_TYPE" = "sqlserver" ]; then \
    echo "--- Installing SQL Server client ---" && \
    apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get purge -y --auto-remove curl gnupg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*; \
    fi

# Copy installed python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
WORKDIR /app

# Copy application code
COPY --chown=app:app . .

# Create and set permissions for directories used by the app
RUN mkdir -p /app/pdfs /app/configs /app/data /app/staticfiles && \
    chown -R app:app /app && \
    chmod -R 755 /app

COPY --chown=app:app entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER app
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]