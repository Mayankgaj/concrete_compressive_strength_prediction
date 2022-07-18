FROM python:3.7
COPY . /app
WORKDIR /app
ARG KAGGLE_USERNAME={{secrets.KAGGLE_USERNAME}}
ARG KAGGLE_KEY={{secrets.KAGGLE_KEY}}
RUN pip install -r requirements.txt
EXPOSE $PORT
CMD gunicorn --workers=1 --bind 0.0.0.0:$PORT app:app -e KAGGLE_USERNAME=$KAGGLE_USERNAME  -e KAGGLE_KEY=$KAGGLE_KEY








