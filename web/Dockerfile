FROM python:3
WORKDIR /usr/src/app
COPY requirements.txt ./
ENV FLASK_APP=src
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
RUN pip install --no-cache-dir -r requirements.txt
CMD ["flask", "run"]
