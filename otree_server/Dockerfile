FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir otree==6.0.13

COPY . .

EXPOSE 8000

CMD ["otree", "prodserver", "8000"]
