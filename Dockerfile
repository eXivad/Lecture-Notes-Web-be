# Stage 1
FROM python:3-slim-buster AS builder

WORKDIR /
COPY . /


RUN python3 -m venv venv
ENV VIRTUAL_ENV=venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage 2
FROM python:3-slim-buster AS runner

WORKDIR /

COPY --from=builder /venv venv
COPY . /

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV FLASK_APP=app.py

EXPOSE 8000

CMD ["python", "app.py"]