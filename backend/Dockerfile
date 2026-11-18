# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Reuse this layer until the requirements change. The pip cache also avoids
# downloading unchanged packages when rebuilding the dependency layer.
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .

# A fresh checkout does not contain the model required by Application.
# Reuse a supplied model, or train it from the checked-in dataset.
RUN if [ ! -f models/rul_random_forest.joblib ]; then \
      python -m demos.evaluate_final_rul_model; \
    fi

RUN useradd --create-home --uid 10001 twinforge \
    && mkdir -p /app/storage \
    && chown -R twinforge:twinforge /app/storage

USER twinforge
EXPOSE 8000

# One worker owns the simulation and SQLite connection.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
