FROM python:3.10

WORKDIR /app
COPY . .

RUN apt update && apt install -y ffmpeg
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
