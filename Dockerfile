#e the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

WORKDIR /app
COPY . main.py /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD [ "main.py" ]
ENTRYPOINT [ "python" ]