FROM python:3.12

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir pip-tools && \
    pip-sync --pip-args "--timeout 100" && \
    pip uninstall -y pip-tools

COPY . .

RUN mkdir -p flasgger_static && \
    cp -r /usr/local/lib/python3.12/site-packages/flasgger/ui3/static/* flasgger_static

# ENV vars can be overridden by docker compose / .env file
ENV APP_PORT=8000
ENV N_WORKERS=3
ENV MAX_REQUESTS=1000
CMD echo "RUNTIME: APP_PORT=${APP_PORT}, N_WORKERS=${N_WORKERS}, MAX_REQUESTS=${MAX_REQUESTS}" && gunicorn --bind "0.0.0.0:${APP_PORT}" --workers ${N_WORKERS} --max-requests ${MAX_REQUESTS} --reload app:app