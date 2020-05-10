FROM python:3.8-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

USER 1000:1000
COPY . .

EXPOSE 8000

#CMD [ "python", "./your-daemon-or-script.py" ]
CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
