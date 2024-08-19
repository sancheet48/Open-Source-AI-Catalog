FROM python:3.11-slim

WORKDIR /code

COPY . /code

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


EXPOSE 80

# Make the deploy script executable
RUN chmod +x scripts/deploy.sh

CMD ["sh", "-c", "scripts/deploy.sh"]
