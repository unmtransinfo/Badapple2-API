FROM python:3.12

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# can be overriden by docker compose
ENV APP_PORT=8000
CMD echo "RUNTIME: APP_PORT is set to ${APP_PORT}" && gunicorn --bind "0.0.0.0:${APP_PORT}" --reload app:app