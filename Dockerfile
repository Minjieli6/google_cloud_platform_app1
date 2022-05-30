#e the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

RUN pip install -r requirements.txt
EXPOSE 8080
CMD [ "main.py" ]
ENTRYPOINT ["gunicorn","--bind=0.0.0.0:8080","main:server"]