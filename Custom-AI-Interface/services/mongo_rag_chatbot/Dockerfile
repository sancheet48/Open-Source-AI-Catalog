FROM python:3.11-slim

WORKDIR /code

COPY ./query_bot /code/query_bot
COPY ./requirements.txt /code/requirements.txt


RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


EXPOSE 80
ENTRYPOINT ["uvicorn", "query_bot.main:api", "--host", "0.0.0.0", "--port", "80"]
CMD ["--workers", "2"]
