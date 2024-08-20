FROM python:3.12

WORKDIR /

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./fastrm ./fastrm

CMD ["celery", "-A", "fastrm", "worker", "-l", "DEBUG"]
