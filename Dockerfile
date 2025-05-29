FROM python:3.10.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

# Make the startup script executable
RUN chmod +x start.sh

EXPOSE 10000

CMD ["./start.sh"]
