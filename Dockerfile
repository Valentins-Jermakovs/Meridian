# ==============================
# Base Image
# ==============================

FROM python:3.14-slim


# ==============================
# Environment Configuration
# ==============================

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


# ==============================
# Working Directory
# ==============================

WORKDIR /app


# ==============================
# Dependencies
# ==============================

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# ==============================
# Application User
# ==============================

RUN groupadd --system app \
    && useradd --system \
        --gid app \
        --home-dir /home/app \
        --shell /usr/sbin/nologin \
        app


# ==============================
# Application Files
# ==============================

COPY app/ .

RUN chmod -R a+rX /app


# ==============================
# Application Port
# ==============================

EXPOSE 8000


# ==============================
# Runtime User
# ==============================

USER app


# ==============================
# Application Startup
# ==============================

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]