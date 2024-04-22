# Stage 1
FROM python:3-slim-buster AS builder

WORKDIR /

RUN python3 -m venv venv
ENV VIRTUAL_ENV=/Lecture-Notes-Web/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage 2
FROM python:3-slim-buster AS runner

WORKDIR /

COPY --from=builder /venv venv
COPY app.py app.py

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["python", "app.py"]