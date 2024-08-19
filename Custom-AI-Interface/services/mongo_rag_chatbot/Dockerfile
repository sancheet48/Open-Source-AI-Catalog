FROM python:3.11-slim

WORKDIR /code

COPY ./mongo_bot /code/mongo_bot
COPY ./requirements.txt /code/requirements.txt


RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


EXPOSE 8000
CMD ["uvicorn", "mongo_bot.main:api", "--host", "0.0.0.0", "--port", "8000"]
