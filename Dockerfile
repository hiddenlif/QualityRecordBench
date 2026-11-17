FROM python:3.12-slim AS solver
WORKDIR /task
USER 65534:65534
CMD ["python", "-m", "json.tool", "/task/cases.json"]

FROM python:3.12-slim AS verifier
WORKDIR /app
COPY qrb/__init__.py qrb/grade.py /app/qrb/
USER 65534:65534
ENTRYPOINT ["python", "-m", "qrb.grade"]
