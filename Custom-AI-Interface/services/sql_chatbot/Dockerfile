FROM curlimages/curl as CERT



FROM python:3.11-slim

WORKDIR /code

COPY . /code

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt



EXPOSE 80
ENTRYPOINT ["uvicorn", "service.main:api", "--host", "0.0.0.0", "--port", "80"]
CMD ["--workers", "2"]
