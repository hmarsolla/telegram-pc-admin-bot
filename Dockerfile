FROM python:3.14-slim

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./main.py ./
COPY ./config.py ./

# Mount .env file as a volume at runtime
# Example: docker run -v $(pwd)/.env:/app/.env telegram-bot

CMD ["python", "main.py"]