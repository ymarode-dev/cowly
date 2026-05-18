# Integration test runner (Python 3.11)
FROM python:3.11-slim

WORKDIR /cowly

COPY requirements-test.txt /cowly/requirements-test.txt
RUN pip install --no-cache-dir -r /cowly/requirements-test.txt

COPY integration /cowly/integration
COPY pytest.ini /cowly/pytest.ini

ENV COWLY_GATEWAY_URL=http://api-gateway:8000

CMD ["pytest", "-q", "integration/", "-m", "integration"]
