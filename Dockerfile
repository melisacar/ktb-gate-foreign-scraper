FROM apache/airflow:latest

# UTF-8 settings.
ENV PYTHONUTF8=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV ENV=docker

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt