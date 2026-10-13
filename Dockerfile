FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt requirements-build.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt -r requirements-build.txt
COPY helper /app/helper
RUN python -m build --wheel --no-isolation /app/helper && python -m pip install --no-deps /app/helper/dist/alert_helper-0.1.0-py3-none-any.whl
COPY . /app
ENV PYTHONDONTWRITEBYTECODE=1
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
