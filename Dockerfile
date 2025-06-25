# Multi-stage build for Guest Registration System
FROM python:3.11-slim AS builder

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install comprehensive build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core build tools
    build-essential \
    gcc \
    g++ \
    pkg-config \
    curl \
    # PostgreSQL development
    libpq-dev \
    postgresql-client \
    # Core system libraries
    libffi-dev \
    libssl-dev \
    # Image processing - COMPLETE development packages
    libjpeg62-turbo-dev \
    libpng-dev \
    libfreetype6-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    liblcms2-dev \
    libxcb1-dev \
    # Font and rendering system
    libfontconfig1-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Force build critical packages from source to ensure proper compilation
RUN pip install --no-cache-dir --force-reinstall --no-binary=:all: \
    cffi>=1.15.1 \
    Pillow>=10.0.1

# Install WeasyPrint after ensuring dependencies are built
RUN pip install --no-cache-dir --force-reinstall WeasyPrint==60.2 pydyf==0.10.0

# Verify critical modules during build
RUN python -c "import PIL; from PIL import _imaging; print('Pillow _imaging OK')"
RUN python -c "import cffi; print('cffi OK')"
RUN python -c "import weasyprint; print('WeasyPrint OK')"

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH" \
    # Font configuration
    FONTCONFIG_PATH=/etc/fonts \
    FONTCONFIG_FILE=/etc/fonts/fonts.conf \
    # Flask configuration
    FLASK_APP=app.py \
    FLASK_ENV=production

# Install runtime dependencies - EXACT versions matching build stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core utilities
    curl \
    # PostgreSQL runtime
    libpq5 \
    postgresql-client \
    # Core system libraries - runtime versions
    libffi8 \
    libssl3 \
    # Image processing - EXACT runtime libraries
    libjpeg62-turbo \
    libpng16-16 \
    libfreetype6 \
    libtiff6 \
    libwebp7 \
    libopenjp2-7 \
    zlib1g \
    liblcms2-2 \
    libxcb1 \
    # Font and rendering system - runtime
    libfontconfig1 \
    fontconfig \
    fonts-freefont-ttf \
    fonts-liberation2 \
    fonts-dejavu-core \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Create application user with proper home directory
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /home/appuser -s /bin/bash -m appuser

# Create application directories with proper ownership
RUN mkdir -p /app /opt/venv && \
    chown -R appuser:appuser /app /home/appuser

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Setup font cache and permissions as root
RUN mkdir -p /var/cache/fontconfig /home/appuser/.cache/fontconfig /home/appuser/.cache/pip && \
    chown -R appuser:appuser /home/appuser/.cache && \
    chmod -R 755 /home/appuser/.cache && \
    fc-cache -fv

# Switch to application user
USER appuser
WORKDIR /app

# Set HOME environment for appuser
ENV HOME=/home/appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p uploads static/uploads logs

# Final verification of all components
RUN python -c "import sys; print(f'Python: {sys.version}'); import PIL; from PIL import Image, _imaging, ImageOps, ImageFile; print(f'Pillow: {PIL.__version__} - _imaging module OK'); import cffi; print(f'cffi: {cffi.__version__}'); import weasyprint; from weasyprint import HTML, CSS; from weasyprint.text.fonts import FontConfiguration; print(f'WeasyPrint: {weasyprint.__version__}'); print('All components verified successfully!')"

# Make scripts executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/health/readiness || exit 1

# Use entrypoint script
ENTRYPOINT ["./entrypoint.sh"]