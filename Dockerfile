from python:3.7.3-alpine3.9

RUN mkdir /app
COPY brs.py /app
COPY environment.txt /app
RUN pip install -r /app/environment.txt

ENTRYPOINT ["python", "/app/brs.py"]