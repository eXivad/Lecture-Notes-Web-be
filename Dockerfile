# Stage 1
FROM python:3-slim-buster AS builder

WORKDIR /Lecture-Notes-Web

RUN python3 -m venv venv
ENV VIRTUAL_ENV=/Lecture-Notes-Web/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage 2
FROM python:3-slim-buster AS runner

WORKDIR /Lecture-Notes-Web

COPY --from=builder /Lecture-Notes-Web/venv venv
COPY app.py app.py

ENV VIRTUAL_ENV=/Lecture-Notes-Web/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["gunicorn" "-k" "geventwebsocket.gunicorn.workers.GeventWebSocketWorker" "-w" "1" "module:app"]