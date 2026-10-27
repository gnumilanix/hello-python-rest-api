FROM python:3.14-alpine AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1"

COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

FROM python:3.14-alpine AS runner

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade "setuptools>=78.1.1"

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY src/ ./src/
COPY jetbase/ ./jetbase/

EXPOSE 8000

CMD ["uvicorn", "necktie.main:app", "--host", "0.0.0.0", "--port", "8000"]
