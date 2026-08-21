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
# Application Files
# ==============================

COPY app/ .


# ==============================
# Application Port
# ==============================

EXPOSE 8000


# ==============================
# Application Startup
# ==============================

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]